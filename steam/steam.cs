//==============================================================================
// STEAM STORE CONNECTOR - C# Implementation
// Connects to https://store.steampowered.com/
// Uses mathematical analysis for game data processing
//==============================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using MathNet.Numerics;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.Statistics;
using MathNet.Numerics.Distributions;
using MathNet.Numerics.Optimization;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace SteamStoreConnector
{
    //==========================================================================
    // MATHEMATICAL FOUNDATIONS
    //==========================================================================
    
    /// <summary>
    /// Linear Algebra operations for game feature vectors
    /// </summary>
    public class GameFeatureVector
    {
        public string GameName { get; set; }
        public Vector<double> Features { get; set; }
        
        public GameFeatureVector(string name, double[] features)
        {
            GameName = name;
            Features = Vector<double>.Build.DenseOfArray(features);
        }
        
        public double DotProduct(GameFeatureVector other)
        {
            return Features.DotProduct(other.Features);
        }
        
        public double Magnitude => Features.L2Norm();
        
        public double CosineSimilarity(GameFeatureVector other)
        {
            double dot = DotProduct(other);
            double mag = Magnitude * other.Magnitude;
            return mag > 0 ? dot / mag : 0;
        }
        
        public GameFeatureVector Normalize()
        {
            double mag = Magnitude;
            return new GameFeatureVector(GameName, 
                Features.Select(f => f / mag).ToArray());
        }
    }
    
    /// <summary>
    /// Statistical analysis for Steam game data
    /// </summary>
    public class SteamStatistics
    {
        public static double CalculateMean(IEnumerable<double> values)
        {
            return values.Mean();
        }
        
        public static double CalculateMedian(IEnumerable<double> values)
        {
            return values.Median();
        }
        
        public static double CalculateStandardDeviation(IEnumerable<double> values)
        {
            return values.StandardDeviation();
        }
        
        public static double CalculateSkewness(IEnumerable<double> values)
        {
            return values.Skewness();
        }
        
        public static double CalculateKurtosis(IEnumerable<double> values)
        {
            return values.Kurtosis();
        }
        
        /// <summary>
        /// Bayesian Wilson Score for rating confidence
        /// </summary>
        public static double WilsonScore(double positive, double total, double z = 1.96)
        {
            if (total == 0) return 0;
            double p = positive / total;
            double z2 = z * z;
            double denominator = 1 + z2 / total;
            double center = (p + z2 / (2 * total)) / denominator;
            double margin = z * Math.Sqrt((p * (1 - p) + z2 / (4 * total)) / total) / denominator;
            return center - margin;
        }
        
        /// <summary>
        /// Gaussian Mixture Model for game clustering
        /// </summary>
        public static (double[] means, double[] weights) FitGMM(double[] data, int components = 3, int iterations = 100)
        {
            int n = data.Length;
            var random = new Random(42);
            
            // Initialize parameters
            double[] means = new double[components];
            double[] variances = new double[components];
            double[] weights = new double[components];
            
            for (int i = 0; i < components; i++)
            {
                means[i] = data[random.Next(n)];
                variances[i] = data.Variance();
                weights[i] = 1.0 / components;
            }
            
            // EM algorithm
            for (int iter = 0; iter < iterations; iter++)
            {
                double[,] responsibilities = new double[n, components];
                
                // E-step
                for (int i = 0; i < n; i++)
                {
                    double sum = 0;
                    for (int k = 0; k < components; k++)
                    {
                        double pdf = weights[k] * Normal.PDF(means[k], Math.Sqrt(variances[k]), data[i]);
                        responsibilities[i, k] = pdf;
                        sum += pdf;
                    }
                    
                    for (int k = 0; k < components; k++)
                    {
                        responsibilities[i, k] /= sum;
                    }
                }
                
                // M-step
                for (int k = 0; k < components; k++)
                {
                    double nk = 0;
                    double sumResp = 0;
                    double sumRespSq = 0;
                    
                    for (int i = 0; i < n; i++)
                    {
                        nk += responsibilities[i, k];
                        sumResp += responsibilities[i, k] * data[i];
                    }
                    
                    means[k] = sumResp / nk;
                    weights[k] = nk / n;
                    
                    for (int i = 0; i < n; i++)
                    {
                        double diff = data[i] - means[k];
                        sumRespSq += responsibilities[i, k] * diff * diff;
                    }
                    variances[k] = sumRespSq / nk;
                }
            }
            
            return (means, weights);
        }
    }
    
    /// <summary>
    /// Optimization algorithms for game recommendations
    /// </summary>
    public class RecommendationOptimizer
    {
        /// <summary>
        /// Gradient Descent for weight optimization
        /// </summary>
        public static double[] GradientDescent(
            List<GameFeatureVector> games,
            double[] targetScores,
            double learningRate = 0.01,
            int maxIterations = 1000)
        {
            int numFeatures = games[0].Features.Count;
            double[] weights = Enumerable.Repeat(1.0 / numFeatures, numFeatures).ToArray();
            
            for (int iter = 0; iter < maxIterations; iter++)
            {
                double[] gradient = new double[numFeatures];
                double totalError = 0;
                
                for (int i = 0; i < games.Count; i++)
                {
                    double prediction = 0;
                    for (int j = 0; j < numFeatures; j++)
                    {
                        prediction += weights[j] * games[i].Features[j];
                    }
                    
                    double error = prediction - targetScores[i];
                    totalError += error * error;
                    
                    for (int j = 0; j < numFeatures; j++)
                    {
                        gradient[j] += error * games[i].Features[j];
                    }
                }
                
                if (totalError < 1e-6) break;
                
                for (int j = 0; j < numFeatures; j++)
                {
                    weights[j] -= learningRate * gradient[j] / games.Count;
                }
            }
            
            return weights;
        }
        
        /// <summary>
        /// Newton's Method for finding optimal pricing
        /// </summary>
        public static double NewtonMethod(Func<double, double> f, Func<double, double> df,
            double initialGuess, double tolerance = 1e-6, int maxIterations = 100)
        {
            double x = initialGuess;
            
            for (int i = 0; i < maxIterations; i++)
            {
                double fx = f(x);
                double dfx = df(x);
                
                if (Math.Abs(dfx) < 1e-10) break;
                
                double xNew = x - fx / dfx;
                
                if (Math.Abs(xNew - x) < tolerance) return xNew;
                x = xNew;
            }
            
            return x;
        }
    }
    
    //==========================================================================
    // STEAM STORE DATA MODELS
    //==========================================================================
    
    public class SteamGameInfo
    {
        public string AppId { get; set; }
        public string Name { get; set; }
        public double Price { get; set; }
        public double OriginalPrice { get; set; }
        public int DiscountPercent { get; set; }
        public List<string> Tags { get; set; } = new List<string>();
        public string ReleaseDate { get; set; }
        public double ReviewScore { get; set; }
        public int TotalReviews { get; set; }
        public string Developer { get; set; }
        public string Publisher { get; set; }
        public string Description { get; set; }
        public string HeaderImage { get; set; }
        
        public double[] ToFeatureVector()
        {
            return new double[]
            {
                Price / 100.0, // Normalize price
                OriginalPrice > 0 ? Price / OriginalPrice : 1.0,
                DiscountPercent / 100.0,
                ReviewScore / 100.0,
                Math.Log1p(TotalReviews) / 15.0,
                Math.Min(Tags.Count / 20.0, 1.0),
                (DateTime.Now - DateTime.Parse(ReleaseDate ?? "2020-01-01")).TotalDays / 3650.0
            };
        }
    }
    
    //==========================================================================
    // STEAM STORE HTTP CLIENT
    //==========================================================================
    
    public class SteamStoreClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private const string BaseUrl = "https://store.steampowered.com";
        private const string ApiBaseUrl = "https://store.steampowered.com/api";
        
        public SteamStoreClient()
        {
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Add("User-Agent", 
                "SteamStoreConnector/1.0 (compatible; MSIE 10.0; Windows NT 6.2)");
            _httpClient.DefaultRequestHeaders.Add("Accept", "application/json");
            _httpClient.DefaultRequestHeaders.Add("Accept-Language", "en-US,en;q=0.9");
        }
        
        /// <summary>
        /// Search games on Steam store
        /// </summary>
        public async Task<List<SteamGameInfo>> SearchGamesAsync(string query, int maxResults = 50)
        {
            var games = new List<SteamGameInfo>();
            
            try
            {
                string url = $"{BaseUrl}/search/results/?term={Uri.EscapeDataString(query)}&max={maxResults}";
                string response = await _httpClient.GetStringAsync(url);
                
                // Parse HTML response for game data
                var appIdRegex = new Regex(@"data-ds-appid=""(\d+)""");
                var titleRegex = new Regex(@"<span class=""title"">([^<]+)</span>");
                var priceRegex = new Regex(@"(\d+\.?\d*)");
                var reviewRegex = new Regex(@"data-tooltip-html=""(\d+)%");
                
                var appIdMatches = appIdRegex.Matches(response);
                var titleMatches = titleRegex.Matches(response);
                
                for (int i = 0; i < Math.Min(appIdMatches.Count, titleMatches.Count); i++)
                {
                    var game = new SteamGameInfo
                    {
                        AppId = appIdMatches[i].Groups[1].Value,
                        Name = System.Net.WebUtility.HtmlDecode(titleMatches[i].Groups[1].Value)
                    };
                    games.Add(game);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Search error: {ex.Message}");
            }
            
            return games;
        }
        
        /// <summary>
        /// Get featured games from Steam homepage
        /// </summary>
        public async Task<List<SteamGameInfo>> GetFeaturedGamesAsync()
        {
            var games = new List<SteamGameInfo>();
            
            try
            {
                string url = $"{ApiBaseUrl}/featured/";
                string response = await _httpClient.GetStringAsync(url);
                var data = JObject.Parse(response);
                
                foreach (var item in data["featured_win"] ?? new JArray())
                {
                    var game = new SteamGameInfo
                    {
                        AppId = item["id"]?.ToString(),
                        Name = item["name"]?.ToString(),
                        Price = (double)(item["final_price"] ?? 0) / 100.0,
                        OriginalPrice = (double)(item["initial_price"] ?? 0) / 100.0,
                        DiscountPercent = (int)(item["discount_percent"] ?? 0),
                        HeaderImage = item["large_capsule_image"]?.ToString()
                    };
                    games.Add(game);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Featured games error: {ex.Message}");
            }
            
            return games;
        }
        
        /// <summary>
        /// Get detailed app information via Steam API
        /// </summary>
        public async Task<SteamGameInfo> GetAppDetailsAsync(string appId)
        {
            try
            {
                string url = $"{ApiBaseUrl}/appdetails?appids={appId}";
                string response = await _httpClient.GetStringAsync(url);
                var data = JObject.Parse(response);
                
                var appData = data[appId];
                if (appData["success"].Value<bool>())
                {
                    var details = appData["data"];
                    var game = new SteamGameInfo
                    {
                        AppId = appId,
                        Name = details["name"]?.ToString(),
                        Description = details["short_description"]?.ToString(),
                        Developer = details["developers"]?.First?.ToString(),
                        Publisher = details["publishers"]?.First?.ToString(),
                        ReleaseDate = details["release_date"]?["date"]?.ToString(),
                        HeaderImage = details["header_image"]?.ToString()
                    };
                    
                    if (details["price_overview"] != null)
                    {
                        game.Price = details["price_overview"]["final"].Value<double>() / 100.0;
                        game.OriginalPrice = details["price_overview"]["initial"].Value<double>() / 100.0;
                        game.DiscountPercent = details["price_overview"]["discount_percent"].Value<int>();
                    }
                    
                    if (details["genres"] != null)
                    {
                        foreach (var genre in details["genres"])
                        {
                            game.Tags.Add(genre["description"]?.ToString());
                        }
                    }
                    
                    return game;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"App details error for {appId}: {ex.Message}");
            }
            
            return null;
        }
        
        /// <summary>
        /// Get current Steam store deals
        /// </summary>
        public async Task<List<SteamGameInfo>> GetStoreDealsAsync()
        {
            var games = new List<SteamGameInfo>();
            
            try
            {
                string url = $"{BaseUrl}/search/results/?specials=1&max=100";
                string response = await _httpClient.GetStringAsync(url);
                
                // Parse deals from response
                var appIdRegex = new Regex(@"data-ds-appid=""(\d+)""");
                var discountRegex = new Regex(@"-(\d+)%");
                var priceRegex = new Regex(@"CDN\$ (\d+\.\d+)");
                var originalPriceRegex = new Regex(@"CDN\$ (\d+\.\d+)");
                
                var matches = appIdRegex.Matches(response);
                foreach (Match match in matches)
                {
                    var game = new SteamGameInfo
                    {
                        AppId = match.Groups[1].Value
                    };
                    games.Add(game);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Deals error: {ex.Message}");
            }
            
            return games;
        }
        
        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
    
    //==========================================================================
    // MATHEMATICAL GAME ANALYZER
    //==========================================================================
    
    public class GameAnalyzer
    {
        private readonly List<SteamGameInfo> _games;
        
        public GameAnalyzer(List<SteamGameInfo> games)
        {
            _games = games;
        }
        
        /// <summary>
        /// Perform comprehensive mathematical analysis
        /// </summary>
        public AnalysisReport Analyze()
        {
            var report = new AnalysisReport();
            
            // Price analysis
            var prices = _games.Where(g => g.Price > 0).Select(g => g.Price).ToList();
            report.PriceStatistics = new PriceStats
            {
                Mean = SteamStatistics.CalculateMean(prices),
                Median = SteamStatistics.CalculateMedian(prices),
                StandardDeviation = SteamStatistics.CalculateStandardDeviation(prices),
                Skewness = SteamStatistics.CalculateSkewness(prices),
                Kurtosis = SteamStatistics.CalculateKurtosis(prices),
                Min = prices.Min(),
                Max = prices.Max(),
                Count = prices.Count
            };
            
            // Review analysis
            var reviews = _games.Where(g => g.TotalReviews > 0)
                .Select(g => g.ReviewScore).ToList();
            report.ReviewStatistics = new ReviewStats
            {
                MeanScore = SteamStatistics.CalculateMean(reviews),
                MedianScore = SteamStatistics.CalculateMedian(reviews),
                StdDevScore = SteamStatistics.CalculateStandardDeviation(reviews)
            };
            
            // Bayesian analysis
            report.BayesianRatings = _games
                .Where(g => g.TotalReviews > 0)
                .Select(g => new BayesianRating
                {
                    GameName = g.Name,
                    WilsonScore = SteamStatistics.WilsonScore(
                        g.ReviewScore * g.TotalReviews / 100.0,
                        g.TotalReviews
                    )
                })
                .OrderByDescending(r => r.WilsonScore)
                .ToList();
            
            // Game similarity matrix using cosine similarity
            var featureVectors = _games
                .Select(g => new GameFeatureVector(g.Name, g.ToFeatureVector()))
                .ToList();
            
            report.SimilarityMatrix = new List<SimilarityPair>();
            for (int i = 0; i < Math.Min(featureVectors.Count, 10); i++)
            {
                for (int j = i + 1; j < Math.Min(featureVectors.Count, 10); j++)
                {
                    report.SimilarityMatrix.Add(new SimilarityPair
                    {
                        GameA = featureVectors[i].GameName,
                        GameB = featureVectors[j].GameName,
                        CosineSimilarity = featureVectors[i].CosineSimilarity(featureVectors[j])
                    });
                }
            }
            
            // Clustering using GMM
            if (prices.Count >= 10)
            {
                var (means, weights) = SteamStatistics.FitGMM(prices.ToArray(), 3);
                report.PriceClusters = means.Select((m, i) => new PriceCluster
                {
                    Mean = m,
                    Weight = weights[i],
                    Category = i == 0 ? "Budget" : i == 1 ? "Mid-range" : "Premium"
                }).ToList();
            }
            
            return report;
        }
        
        /// <summary>
        /// Generate optimized recommendations
        /// </summary>
        public List<SteamGameInfo> GetRecommendations(double[] userPreferences, int count = 10)
        {
            var featureVectors = _games
                .Select(g => new GameFeatureVector(g.Name, g.ToFeatureVector()))
                .ToList();
            
            // Generate target scores (simulated user preferences)
            var targetScores = _games.Select(g => 
                g.ReviewScore / 100.0 * 0.4 + 
                (1.0 - g.Price / 100.0) * 0.3 + 
                (g.DiscountPercent / 100.0) * 0.3
            ).ToArray();
            
            // Optimize weights
            var optimizedWeights = RecommendationOptimizer.GradientDescent(
                featureVectors, targetScores);
            
            // Score all games
            var scored = _games.Select((g, i) => new
            {
                Game = g,
                Score = g.ToFeatureVector()
                    .Zip(optimizedWeights, (f, w) => f * w)
                    .Sum()
            })
            .OrderByDescending(x => x.Score)
            .Take(count)
            .Select(x => x.Game)
            .ToList();
            
            return scored;
        }
        
        /// <summary>
        /// Find optimal price point using Newton's Method
        /// </summary>
        public double FindOptimalPrice(double initialGuess = 30.0)
        {
            var prices = _games.Where(g => g.Price > 0).Select(g => g.Price).ToList();
            
            // Revenue function R(p) = p * D(p) where D(p) is demand
            double DemandFunction(double p)
            {
                // Simplified demand curve based on historical data
                double baseDemand = 1000;
                double elasticity = -1.5;
                return baseDemand * Math.Pow(p / 60.0, elasticity);
            }
            
            double RevenueFunction(double p) => p * DemandFunction(p);
            
            double RevenueDerivative(double p)
            {
                double h = 0.01;
                return (RevenueFunction(p + h) - RevenueFunction(p - h)) / (2 * h);
            }
            
            return RecommendationOptimizer.NewtonMethod(
                RevenueDerivative,
                p => (RevenueDerivative(p + 0.01) - RevenueDerivative(p - 0.01)) / 0.02,
                initialGuess
            );
        }
    }
    
    //==========================================================================
    // ANALYSIS REPORT MODELS
    //==========================================================================
    
    public class AnalysisReport
    {
        public PriceStats PriceStatistics { get; set; }
        public ReviewStats ReviewStatistics { get; set; }
        public List<BayesianRating> BayesianRatings { get; set; }
        public List<SimilarityPair> SimilarityMatrix { get; set; }
        public List<PriceCluster> PriceClusters { get; set; }
    }
    
    public class PriceStats
    {
        public double Mean { get; set; }
        public double Median { get; set; }
        public double StandardDeviation { get; set; }
        public double Skewness { get; set; }
        public double Kurtosis { get; set; }
        public double Min { get; set; }
        public double Max { get; set; }
        public int Count { get; set; }
    }
    
    public class ReviewStats
    {
        public double MeanScore { get; set; }
        public double MedianScore { get; set; }
        public double StdDevScore { get; set; }
    }
    
    public class BayesianRating
    {
        public string GameName { get; set; }
        public double WilsonScore { get; set; }
    }
    
    public class SimilarityPair
    {
        public string GameA { get; set; }
        public string GameB { get; set; }
        public double CosineSimilarity { get; set; }
    }
    
    public class PriceCluster
    {
        public double Mean { get; set; }
        public double Weight { get; set; }
        public string Category { get; set; }
    }
    
    //==========================================================================
    // MAIN PROGRAM
    //==========================================================================
    
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("========================================");
            Console.WriteLine("  Steam Store Connector - C# Edition");
            Console.WriteLine("  Mathematical Analysis Engine");
            Console.WriteLine("========================================\n");
            
            using var client = new SteamStoreClient();
            var allGames = new List<SteamGameInfo>();
            
            // 1. Connect to Steam store
            Console.WriteLine("[1] Connecting to store.steampowered.com...");
            var featured = await client.GetFeaturedGamesAsync();
            Console.WriteLine($"  ✓ Found {featured.Count} featured games");
            allGames.AddRange(featured);
            
            // 2. Search for games
            Console.WriteLine("\n[2] Searching for games by genre...");
            string[] queries = { "RPG", "Strategy", "Action", "Indie" };
            foreach (var query in queries)
            {
                var results = await client.SearchGamesAsync(query, 20);
                Console.WriteLine($"  ✓ {query}: {results.Count} results");
                allGames.AddRange(results);
            }
            
            // 3. Get detailed information for top games
            Console.WriteLine("\n[3] Fetching detailed game information...");
            var topAppIds = featured.Take(5).Select(g => g.AppId).ToList();
            foreach (var appId in topAppIds)
            {
                var details = await client.GetAppDetailsAsync(appId);
                if (details != null)
                {
                    Console.WriteLine($"  ✓ {details.Name}");
                    var existing = allGames.FirstOrDefault(g => g.AppId == appId);
                    if (existing != null) allGames.Remove(existing);
                    allGames.Add(details);
                }
            }
            
            // 4. Get store deals
            Console.WriteLine("\n[4] Checking current Steam deals...");
            var deals = await client.GetStoreDealsAsync();
            Console.WriteLine($"  ✓ Found {deals.Count} games on sale");
            
            // 5. Mathematical analysis
            Console.WriteLine("\n[5] Performing mathematical analysis...");
            var analyzer = new GameAnalyzer(allGames.DistinctBy(g => g.AppId).ToList());
            var report = analyzer.Analyze();
            
            Console.WriteLine("\n=== ANALYSIS RESULTS ===");
            Console.WriteLine($"\nPrice Statistics:");
            Console.WriteLine($"  Mean: ${report.PriceStatistics.Mean:F2}");
            Console.WriteLine($"  Median: ${report.PriceStatistics.Median:F2}");
            Console.WriteLine($"  Std Dev: ${report.PriceStatistics.StandardDeviation:F2}");
            Console.WriteLine($"  Skewness: {report.PriceStatistics.Skewness:F3}");
            Console.WriteLine($"  Min: ${report.PriceStatistics.Min:F2}");
            Console.WriteLine($"  Max: ${report.PriceStatistics.Max:F2}");
            
            Console.WriteLine($"\nReview Statistics:");
            Console.WriteLine($"  Mean Score: {report.ReviewStatistics.MeanScore:F1}%");
            Console.WriteLine($"  Median Score: {report.ReviewStatistics.MedianScore:F1}%");
            
            Console.WriteLine($"\nTop 5 Games by Bayesian Rating:");
            foreach (var rating in report.BayesianRatings.Take(5))
            {
                Console.WriteLine($"  {rating.GameName}: {rating.WilsonScore:F3}");
            }
            
            Console.WriteLine($"\nGame Similarities (Cosine):");
            foreach (var pair in report.SimilarityMatrix.Take(5))
            {
                Console.WriteLine($"  {pair.GameA} ↔ {pair.GameB}: {pair.CosineSimilarity:F3}");
            }
            
            if (report.PriceClusters != null)
            {
                Console.WriteLine($"\nPrice Clusters (GMM):");
                foreach (var cluster in report.PriceClusters)
                {
                    Console.WriteLine($"  {cluster.Category}: ${cluster.Mean:F2} (weight: {cluster.Weight:F2})");
                }
            }
            
            // 6. Generate recommendations
            Console.WriteLine("\n[6] Generating optimized recommendations...");
            var userPrefs = new[] { 0.3, 0.8, 0.5, 0.9, 0.4, 0.6, 0.2 };
            var recommendations = analyzer.GetRecommendations(userPrefs, 5);
            
            Console.WriteLine("\n=== TOP RECOMMENDATIONS ===");
            for (int i = 0; i < recommendations.Count; i++)
            {
                Console.WriteLine($"  {i + 1}. {recommendations[i].Name}");
                if (recommendations[i].Price > 0)
                    Console.WriteLine($"     ${recommendations[i].Price:F2}");
            }
            
            // 7. Find optimal pricing
            Console.WriteLine("\n[7] Computing optimal price point...");
            double optimalPrice = analyzer.FindOptimalPrice(30.0);
            Console.WriteLine($"  Optimal price: ${optimalPrice:F2}");
            
            Console.WriteLine("\n✓ Steam Store connection and analysis complete.");
        }
    }
}