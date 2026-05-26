using RuriLib.Logging;
using RuriLib.Models.Blocks;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace RuriLib.Blocks.Datadome
{
    [BlockCategory("Datadome")]
    [BlockName("Datadome Solver")]
    [BlockDescription("Solves Datadome captcha challenges")]
    public class DatadomeSolverBlock : BlockBase
    {
        private static readonly HttpClient httpClient = new HttpClient();

        [BlockOption(description: "Target URL (e.g., https://www.etsy.com/)")]
        public string TargetUrl { get; set; } = "https://www.etsy.com/";

        [BlockOption(description: "Datadome JS Key")]
        public string DdJsKey { get; set; } = "D013AA612AB2224D03B2318D0F5B19";

        [BlockOption(description: "Challenge ID (from dd-cid cookie or response)")]
        public string Cid { get; set; } = "";

        [BlockOption(description: "Browser profile: chrome_win10, chrome_win10_de")]
        public string Profile { get; set; } = "chrome_win10";

        [BlockOption(description: "Python solver service URL")]
        public string ServiceUrl { get; set; } = "http://localhost:5000";

        [BlockOption(description: "Timeout in seconds")]
        public int TimeoutSeconds { get; set; } = 30;

        public override async Task Execute()
        {
            try
            {
                Logger.LogInfo("[Datadome] Starting solver...");

                // Build request
                var request = new
                {
                    url = TargetUrl,
                    ddjskey = DdJsKey,
                    cid = Cid,
                    profile = Profile
                };

                var json = Newtonsoft.Json.JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                // Set timeout
                httpClient.Timeout = TimeSpan.FromSeconds(TimeoutSeconds);

                // Call solver service
                var serviceUri = $"{ServiceUrl.TrimEnd('/')}/solve";
                Logger.LogInfo($"[Datadome] Calling service: {serviceUri}");

                var response = await httpClient.PostAsync(serviceUri, content);
                var responseContent = await response.Content.ReadAsStringAsync();

                Logger.LogInfo($"[Datadome] Response status: {response.StatusCode}");

                // Parse response
                var responseObj = JObject.Parse(responseContent);

                if (responseObj["success"]?.Value<bool>() == true)
                {
                    var cookie = responseObj["cookie"]?.Value<string>();
                    Logger.LogInfo($"[Datadome] ✓ Challenge solved!");
                    Logger.LogInfo($"[Datadome] Cookie: {cookie}");
                    InsertVariable("DatadomeCookie", cookie);
                }
                else
                {
                    var error = responseObj["error"]?.Value<string>() ?? "Unknown error";
                    Logger.LogError($"[Datadome] ✗ Challenge failed: {error}");
                    throw new Exception($"Datadome solver failed: {error}");
                }
            }
            catch (HttpRequestException ex)
            {
                Logger.LogError($"[Datadome] ✗ Connection error: {ex.Message}");
                Logger.LogError($"[Datadome] Make sure solver service is running: python solver_service.py");
                throw;
            }
            catch (Exception ex)
            {
                Logger.LogError($"[Datadome] ✗ Error: {ex.Message}");
                throw;
            }
        }
    }
}
