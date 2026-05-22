import json
import math
import sys
import time
import argparse
from urllib.parse import unquote

SEED_O = 1789537805
SEED_E = 9959949970
ENCRYPT_SEED = 1809053797
IV_XOR_CONST = 11027890091
DEFAULT_V = 741130091


def to_int32(n):
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def to_uint32(n):
    return n & 0xFFFFFFFF


def float64_to_int32(f):
    if math.isnan(f) or math.isinf(f) or f == 0.0:
        return 0
    n = int(f) & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def xorshift32(n):
    n = to_int32(n)
    n = to_int32(n ^ to_int32(n << 13))
    n = to_int32(n ^ (n >> 17))
    n = to_int32(n ^ to_int32(n << 5))
    return n


def hash_l(s):
    if not s:
        return SEED_O
    t = 0
    for ch in s:
        t = to_int32((to_int32(t << 5) - t + ord(ch)))
    return SEED_O if t == 0 else t


class PRNGStream:
    def __init__(self, seed, iv, xor_with_iv=True):
        self.c = to_int32(seed)
        self.e = -1
        self.i = to_int32(iv)
        self.r = xor_with_iv
        self.cached = None

    def next(self, peek=False):
        if self.cached is not None:
            t = self.cached
            self.cached = None
            return t

        self.e += 1
        if self.e > 2:
            self.c = xorshift32(self.c)
            self.e = 0

        shift = 16 - 8 * self.e
        raw = to_int32(self.c) >> shift if shift >= 0 else to_int32(self.c) << (-shift)
        iv_val = 0
        if self.r:
            self.i = to_int32(self.i - 1)
            iv_val = self.i

        t = 255 & (raw ^ iv_val)
        if peek:
            self.cached = t
        return t


def w_encode(n):
    if n > 37:
        return 59 + n
    elif n > 11:
        return 53 + n
    elif n > 1:
        return 46 + n
    else:
        return 50 * n + 45


def w_decode(code):
    if code == 45:
        return 0
    elif code == 95:
        return 1
    elif 48 <= code <= 57:
        return code - 46
    elif 65 <= code <= 90:
        return code - 53
    elif 97 <= code <= 122:
        return code - 59
    else:
        raise ValueError(f"Invalid encoded char: {chr(code)} ({code})")


def utf8_encode(s):
    return list(s.encode('utf-8'))


def utf8_decode(byte_list):
    return bytes(byte_list).decode('utf-8')


def encrypt(signal_dict, ddjskey, cid=None, timestamp_ms=None):
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)

    n_key = to_int32(to_int32(SEED_E) ^ hash_l(ddjskey) ^ DEFAULT_V)

    ts_shifted = to_int32(to_int32(timestamp_ms) >> 3 ^ to_int32(IV_XOR_CONST))
    inner = xorshift32(ts_shifted)
    product = float(inner) * float(SEED_E)
    f = xorshift32(float64_to_int32(product))

    s_prng = PRNGStream(n_key, f, xor_with_iv=True)

    d = []
    first = True
    for key, value in signal_dict.items():
        if not isinstance(key, str) or len(key) == 0:
            continue
        if value is not None and not isinstance(value, (int, float, str, bool)):
            continue

        key_json = json.dumps(key, ensure_ascii=False)
        val_json = json.dumps(value, ensure_ascii=False)

        separator = 123 if first else 44
        d.append(s_prng.next() ^ separator)

        for b in utf8_encode(key_json):
            d.append(b ^ s_prng.next())

        d.append(58 ^ s_prng.next())

        for b in utf8_encode(val_json):
            d.append(b ^ s_prng.next())

        first = False

    cid_str = cid if cid else None
    t_prng = PRNGStream(to_int32(ENCRYPT_SEED ^ hash_l(cid_str)), f, xor_with_iv=False)

    c = [byte ^ t_prng.next() for byte in d]
    c.append(125 ^ s_prng.next(peek=True) ^ t_prng.next())

    i_data = c
    r_pos = 0
    output = []
    a_iv = to_int32(f)

    while r_pos < len(i_data):
        b0 = i_data[r_pos] if r_pos < len(i_data) else 0
        b1 = i_data[r_pos + 1] if r_pos + 1 < len(i_data) else 0
        b2 = i_data[r_pos + 2] if r_pos + 2 < len(i_data) else 0

        a_iv = to_int32(a_iv - 1)
        v0 = (255 & a_iv) ^ b0
        a_iv = to_int32(a_iv - 1)
        v1 = (255 & a_iv) ^ b1
        a_iv = to_int32(a_iv - 1)
        v2 = (255 & a_iv) ^ b2

        u_combined = (v0 << 16) | (v1 << 8) | v2

        output.append(chr(w_encode((u_combined >> 18) & 63)))
        output.append(chr(w_encode((u_combined >> 12) & 63)))
        output.append(chr(w_encode((u_combined >> 6) & 63)))
        output.append(chr(w_encode(u_combined & 63)))

        r_pos += 3

    remainder = len(i_data) % 3
    if remainder:
        output = output[:-(3 - remainder)]

    return ''.join(output)


def decrypt(jspl_str, ddjskey, cid=None):
    jspl = unquote(jspl_str.strip().replace('\n', '').replace('\r', '').replace(' ', ''))

    raw_6bit = [w_decode(ord(ch)) for ch in jspl]

    num_chars = len(raw_6bit)
    full_groups = num_chars // 4
    remaining = num_chars % 4

    if remaining == 3:
        orig_byte_count = full_groups * 3 + 2
    elif remaining == 2:
        orig_byte_count = full_groups * 3 + 1
    else:
        orig_byte_count = full_groups * 3

    while len(raw_6bit) % 4 != 0:
        raw_6bit.append(0)

    encoded_bytes = []
    for g in range(len(raw_6bit) // 4):
        combined = (raw_6bit[g*4] << 18) | (raw_6bit[g*4+1] << 12) | (raw_6bit[g*4+2] << 6) | raw_6bit[g*4+3]
        encoded_bytes.append((combined >> 16) & 255)
        encoded_bytes.append((combined >> 8) & 255)
        encoded_bytes.append(combined & 255)

    encoded_bytes = encoded_bytes[:orig_byte_count]

    n_key = to_int32(to_int32(SEED_E) ^ hash_l(ddjskey) ^ DEFAULT_V)
    t_seed = to_int32(ENCRYPT_SEED ^ hash_l(cid))

    for f_low in range(256):
        a_counter = f_low
        c_bytes = []
        for idx in range(len(encoded_bytes)):
            a_counter = (a_counter - 1) & 0xFF
            c_bytes.append(encoded_bytes[idx] ^ a_counter)

        t_test = PRNGStream(t_seed, 0, xor_with_iv=False)
        d_bytes = [b ^ t_test.next() for b in c_bytes]

        s_test = PRNGStream(n_key, f_low, xor_with_iv=True)
        first_byte = d_bytes[0] ^ s_test.next()

        if first_byte == 123:
            s_full = PRNGStream(n_key, f_low, xor_with_iv=True)
            plaintext_bytes = [b ^ s_full.next() for b in d_bytes]

            try:
                text = bytes(plaintext_bytes).decode('utf-8', errors='replace')
                if text.startswith('{') and text.endswith('}'):
                    parsed = json.loads(text)
                    return parsed, f_low, text
            except (json.JSONDecodeError, Exception):
                continue

    return None, None, "Decryption failed"


def main():
    parser = argparse.ArgumentParser(description="DataDome jspl crypto tool")
    parser.add_argument('--decrypt', '-d', metavar='JSPL')
    parser.add_argument('--encrypt', '-e', metavar='JSON_FILE')
    parser.add_argument('--key', '-k', metavar='DDJSKEY')
    parser.add_argument('--cid', '-c', metavar='CID', default=None)
    parser.add_argument('--bruteforce', '-b', metavar='JSPL')
    parser.add_argument('--output', '-o', metavar='FILE', default='jspl_decrypted.json')

    args = parser.parse_args()

    if args.encrypt:
        if not args.key:
            print("ERROR: --key required for encryption")
            sys.exit(1)
        with open(args.encrypt) as fh:
            data = json.load(fh)
        print(encrypt(data, args.key, cid=args.cid))
        return

    sample_jspl = (
        "bdtRTFWmW1bnhdGpuZA6hW20FG9K7iI9fOt9lFlqXq_98uQgKrpD5vemxKbbd9Vas8ugTRD2OeHPlx5U8Jp_k9kYymccPlGvgl9tVIVMZ77nQ2bIbKATCJkAPBTiJxCMQ"
        "MjeD140ItrzyE5O_4a35VSZJVL4Hz0UrAO7hBazsz9BUpP9EtpHLQnxyekjjzI0mLjwNNJf0jHFq9Fcr5lA78QRQ1pWZwkssp8DFXgrMHz-XwKfpCnlF2Xg4BoC5sEXTEZi"
        "D9O-kt0lBDW1mOVzXPQVdm8Rm8M7o4GipoqK3pJc3j1L-ADDOYiRmQgbZRnWwxu_V5EJWg5wmhZRQ4D_YPudpiSNfjh0VXbo0Kqca4xYcLeEHHGwcVpKI3TLol07Aaj7DB"
        "kYLvGZe2BP3CYjI5NHAunqgVVSxmp48ekiOS1XXYVrEfAWYIQLEAafupZuwfLrJd0brCv2sluUSFkvCGA4gV5c_djdf02cqwuKzkPEvIWYOTiJ55G76OloCBC5IRyt8iPQ0oD"
        "mT4XZMm-CClm1kGfBzrPZEquDqnZO1ZtTx5Z2jPqXdmc_syCMIFwLeCXdxeRDU5CqxKWw9_0bSPAD4kj6ycZdaVtN9huOCRAGzv8Agd2-bCEdCRKHVb1l3a0BDiSgFe__8b"
        "8HqvbCPfsxXPMFBgmA_FX81I4bkJ9eJErCY2s_ZAXhtFFL593oj-dVO-nHSkqpP4vS8-d5V_ZKKNb1FeLGqqjlG8X0Wdm-UxHxdmFwDGBugCGSwj-NU1niOQb_EXDDqxv_9"
        "YjzJ6gKzHdPje9tULUKkuAOaj-Y1dyNJqQIKKAltuLPWjh0_DYaCHnZF4XcEDrbQup-xXzwt2fEdsfhoGOqLrhV8VBBjKXzyIpNnkOUHMWg-t5A6Y-jzdSQrbLAfm_bQn_HE"
        "J-0raY0-L0wi5EFklleFerN8ma7gioXejliobNME7Q3gB6U0PRahJCm8mLJweh7WaLUUpxwQLiJ0J3cU-gWDH1j1T-oGkpvmvcG0mS9K1iFFe8cY7DQ_0U9yjQCKUXADYYML"
        "Yllx4S7XTVP7fZiIk8vhS8RutRJsOO5LAlg5_3QJgPXyNn7SziNDUUDT2hZuEE0dGorPL6KNo-j5P8oUD88o_FpDbtpQXFtboQQ6uYOpDV21xkqTwpLJXxqOV03u4llQvSbO"
        "INwjr8p2cyvCVhG9R0Ron4vO9mWgj87uROBp0VyFVKr8x29agq05B8LdNG_xLD8RT3mz7pmSB6yw5Xlt8m49Kv-y-DZhQD2GLF2wO1H0GTgB9PlUawfxnoWp6Nr2v-FCiW5K"
        "xtQaAoOO62NttvVbWKfRh_VtWWbPMRb7U5TdMr4QXhdo9UL8iTjehEC5lXQh_3VFcnMGEhFY41DA08WpBOzYLpIf8LCYD7ZWt012AWaSnm3Rb8D3YXZblXQsBSJHjm_3Xwcd"
        "GPSrgkktJyjSm4WEnxSQoQkzXPU-w9ezgX0_DmymSlNwGHA6BJewV4kyOTRXjebfY1Fo9AHiHWpPfoC_EsGQbllBWZfbYiEro76BLe0W5kgRejFQxLdWuvFpi6b08_YsycJWnn"
        "JJG_b8VCEuvgr2lA7KgUSPQHifWNTBVkjU3msGz0KJWlR9faKjTdPL72l-S6rddIrGHEGXp7-7HLcFiBzrgS7iRzs6sv-LA2nE2F6dWbdoHdUl2W6IdqSaV6xoyeh6cezvAe"
        "Leg7myEhoN_lyl3PQMeAQmZG4v2A1RkvVyV1CeZAHHlvTBuDoOvPrjnQJFj8Qb3o62buFglDlvHc53SBEp4esOhxqvYOif9-P9xT6DtytvOilOq4orwYPP9HWGZ18S5IgGirH"
        "1HueyN6WlvnyYLzFVblqcbBn2nwiQEWGtzEa0PfTwfdiyWMDTvsbHWwYOF09TsYaSNDi2vLYPGwBbsdgvA03xI5fm79CuBPlPMG3hpy_GEMeS6FcRtmcVpmpfATJcXVz26Ui5-"
        "Yo6SmaDSKhPiucvLvlbh1eBL0689r64NJ_q5OWoI71JXo83tdtcO0haXg7cn4_ODlB7Zx5xW0sWSpMKWWDTDIrF7bwZR2sG8YpKnTb9rW09SnIBBeO9MFtPkv8DI9qGxuyzqV"
        "0vVYUHX27Vk9QeNGRfNafLQKXzHS1D9ivv_OL54tbqYBscOoYW9LXhBHROlYAbbBlOsy7V9Kqffo_ZZnvs9SPbqYBzzQbcNX2E6cErruvvOUmL80tUfCsJUaolj04ApSJIb267"
        "7zCUMrLY6vw_eH6g6I99Tgkp-wdywMJo4xgCFIB_Q0YNjnADa4t2Vh7VbVmQWXsdnD_VMXQajN4Jq4V1jJGVFUQ3RBMEoo0JToFM4AAV13qcYoY-X6NW8ied_YH8mpUC26EZ"
        "p0pRUY-YL0_3522UqxbFpAC47ACh9Kp6tQ2zRMKbzFVc_gxAC3IuGvMFi6MTJoGI6obJMter8opxNg-z-544p1VkHFahY9qWM2qq9y8GKs7ZFcNCkSt5gC-VwbYWlkQWJd7HN"
        "tVWGDUaPhATXwZozcDfVtSIoA9KJBiy7SsoU5lf80jyGrdv1mwJ_LhdAP4FoTEloFAyVUhgmzlq7t6fA1HTPicTJNHS6C1FNLM4LrV3iinPITyKuD6P5eVVEn3RvcHKS_OTAC"
        "YI00nDcBjKdnkULiXnuLby5R_FqcpK6MBAU3uWUvidFTXTJ6BCRwQ9ERQstUpl1z_4sfmqVrhaX8wsXjpYQTInrRuI3ZNT1zMn19pHxyqkLyiXHQNZ3_mIk1nuaDuA4gAIhpZp"
        "vshCOO_oIcCM6JEhuUNPCRN4vOVAFCAFC2mDov23ERJMgt8mXoDmUpffvT0_MZ3ODj1SB8LEUjXo4RhtjrboKda-FbamhiDbR2ojtNjJAsLCWBptW-rmsDwljfF94F6ZeHOub5V2"
        "iFOIdPdSL7BxPi0LqAsSgrRaP6aPQonmahFBkNcGYcE1Aqq6nVw2TulcPL0--03XsmkzR2yxl2Jqa1Wp31GWcd6wv-BKQJLso1A24V3EwfhCgGIToQ47sfGUjvcGAE_fp_0OW-u"
        "Vam63uJIrmypO98OFR4hoStLrGJ9QekqJzzbnJPrw8jfiYBe5W6QdgoLjznR7Tx6T8r5F5f20cM8D3FchOGIv68R5ymy-iDRT9bdS2wOrKc5z1tfQOipFz48w2DtusENJ94YO1x"
        "CTvyLx8znC_KEQxO1wXfn8RoWSPeVhU--QFDTv737BdNDzP4Lteq4826Om07F_I7PeRDaa14a8jdGEy1DETtvLQxyDV8dvj-BkK6mdSnNUXsUqVMx1F1GkJDSriboLZd22242R0"
        "ndux_TrddafqBg1NeOolu2nVKE3HFybPTLvum9d1yWhplkqWjktptq34AD8hKZq3iIgBR72rKN9gzIGuZyw_wztDFz6tqts0igcVE9ocO772-rFYH-5ZWOxb7c-PgLNXn-Yq2gn"
        "-yqcSEjz1uCchYK_WeK8cOizegNVMDt6RuZAw5ARU8qUolSEh_KGO1zXbs9YPgelz8NLjcAkwrF2lzd5mf6ovwocetP2_ZIEA5eVlSc3glZo65P7gzaROT8dUGUfhwtdLNgsZu"
        "0PvI4CzFPftgrqbZhFsSAD6gkMLuU43eX0pYuGw0DrYjyruOezgznN_mlZqzU1Kg7UBx4-n9HLoQXar7o5Nx1v__i0M6qBqcelfkV9o13xFNh2Y5prVARQYEumdkWcu8dohUt0i"
        "njX01Kc_EikmAFs688b2tM5Xr4KwWK7HhiPoHB4Sns_yVz37G9Pi5KsxTB3BF62-u4Z1TEFKqvfeQEAX0mvupZ1re2e53_3Z1RsQmaWK0fLuuSRVmQA6JUsOzSagGc5pzCwgZW"
        "hqJ9z-oEKqRfTakAh20t2A1fd0nXvn7o1iTMHyKc07w6M_yL3fZ-_egAMjEMi01DbwnuIVNmnYDkznNhGrAk6p6UyDXJ9XpAHOoCfFZi2V7zEy9VWwvl70DiNwb697ZsYz_kHxl"
        "PgtFhQB9OHmnkIHI7bBsrBu_FqTcEpwrNxqbQ1F_91vo_NQJrN5h250uHijPXHqVN49mNZ7zuiGNEspvsTC5Cq2Rj8CNcJxPa5vIvWmvZRBOAN7Usi5NOo4GySr14o0MGQmBmpW"
        "mlGg2_w0P-_YgYhulGf_lbC4j2Wk55JpE0AFlANgOMojhCarQqshTAr_mz4CP02Crb-VkMkfuJ5bi8EtpTmIr-0El5XwN1g4tVclhHqWZJrZACsYVAat-ZbC9JJH8bs569kUJyz"
        "tYAjxJIZtvuW9V-ShknWPkexOk9vwqEhFVPGWJjnfoSeAeCRfLLpmFPZ1HvKZOxaEIaWJQSfEL6BEkaKkkw6Nuohf7BFVQsjKr5wZ2UA3Nx6qer1qlc9wHAwSD9eiFNJCJ8281O"
        "lEWtPFogr64frGneUku_EL2rCSpQacywyd3UTXLIX818-CLOsVLCie6sXa5rX-nQwbtYPfXFgIAo4uu8ql7Ag3e-jcRDWPr3_Wq971VVSDTe-3q1UK-TpaYxWO8UFmVAuXrnAXGx"
        "Jf78nj4nLe8WOMBcoPnjujqyHkyY7lQXyPsxmZx0T0JYAN5vUyZ1uD3x489W8IQwz60JIIGQDUPYxVtk4fAW6WVvM6GzMJbjo-iZ8t26DYGAFxGXFzULjedvw48EPAkpbfabsC"
        "ADVLOHU0k2r0DUzFMUDAIMAdYY2bLAnDYgu12PVc8NjV883v-CNeKqrUJZOjnWPuUuahWO8WC4aUfriQvenvo4dOH-zpw_Oq2M_usPIoTdyk6h9_uqGGaAeH9Sq2ceFffcq-75E"
        "XdDTE-uuds-SHRqahGlBTDb7CNPhn7ZoijTmkL86nF8jtI6uvuDiyDtO62Ug3FyajVy_F2MonQUtkVJXS7_2uFZkSXOd1HSZerSh7xxTS6HAsJwGitBqIMcVyCpAvy3xCBPKE-ri"
        "jIg8SCWiAEnq8qCKP5jBD8Qq3rkb3w2vNLP9Gq5wBLfYbJ9xQiaTIp46oYc79PzanAyYuvw8nJJUsouzWCUk-lyv_rK2k3P0E7M9pUqOS5HNDD7KRPRcNvb-HiAjK0hVUB5E48"
        "MAg8F7hLlFpa3qdBrtnmp0A5_9ENBrfz1Y30Y0pTBpZxgFYDAZd0gPo2cbf"
    )

    jspl_val = args.decrypt or args.bruteforce or sample_jspl

    if args.decrypt and args.key:
        keys_to_try = [args.key]
    elif args.key:
        keys_to_try = [args.key]
    else:
        keys_to_try = [
            "D013AA612AB2224D03B2318D0F5B19",
            "3655B1B731B0E29BA7DAF046E653BE97",
            "A55FBF4311ED6F1BF9911EB71931D5",
            "4BE2E5C534A8B5A0D968EBCC79D81E",
            "9EE40B052AF7A21697E344B47A1B1C",
            "",
        ]

    cids_to_try = [args.cid] if args.cid is not None else [None, ""]

    for ddjskey in keys_to_try:
        for cid in cids_to_try:
            result, f_low, raw = decrypt(jspl_val, ddjskey, cid=cid)
            if result is not None:
                print(f"[SUCCESS] ddjskey={ddjskey} cid={cid!r} f_low={f_low} signals={len(result)}")
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Saved to {args.output}")
                for k, v in result.items():
                    val_str = str(v)
                    if len(val_str) > 100:
                        val_str = val_str[:97] + "..."
                    print(f"  {k}: {val_str}")
                return

    print("Decryption failed. Use --key with the correct ddjskey.")


if __name__ == "__main__":
    main()
