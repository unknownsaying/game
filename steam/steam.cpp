//==============================================================================
// STEAM STORE CONNECTOR - C++ Implementation
// Connects to https://store.steampowered.com/
// Uses mathematical analysis for game data processing
//==============================================================================

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <random>
#include <sstream>
#include <iomanip>
#include <functional>
#include <memory>
#include <chrono>
#include <thread>
#include <fstream>
#include <regex>

// Platform-specific includes
#ifdef _WIN32
    #include <windows.h>
    #include <winhttp.h>
    #pragma comment(lib, "winhttp.lib")
#else
    #include <curl/curl.h>
#endif

// JSON parsing (nlohmann/json - header-only)
#include "nlohmann/json.hpp"
using json = nlohmann::json;

//==============================================================================
// MATHEMATICAL FOUNDATIONS FOR STEAM DATA ANALYSIS
//==============================================================================

namespace SteamMath {
    
    // Linear Algebra: Vector operations for game feature analysis
    class GameVector {
    public:
        std::vector<double> features;
        std::string gameName;
        
        GameVector(const std::string& name, const std::vector<double>& feat)
            : gameName(name), features(feat) {}
        
        double dot(const GameVector& other) const {
            double result = 0.0;
            for (size_t i = 0; i < std::min(features.size(), other.features.size()); ++i) {
                result += features[i] * other.features[i];
            }
            return result;
        }
        
        double magnitude() const {
            return std::sqrt(dot(*this));
        }
        
        double cosineSimilarity(const GameVector& other) const {
            double mag = magnitude() * other.magnitude();
            return mag > 0 ? dot(other) / mag : 0.0;
        }
        
        GameVector normalize() const {
            double mag = magnitude();
            std::vector<double> normalized;
            for (double f : features) normalized.push_back(f / mag);
            return GameVector(gameName, normalized);
        }
    };
    
    // Statistics: Descriptive statistics for pricing analysis
    class PriceStatistics {
    public:
        static double mean(const std::vector<double>& prices) {
            if (prices.empty()) return 0.0;
            return std::accumulate(prices.begin(), prices.end(), 0.0) / prices.size();
        }
        
        static double median(std::vector<double> prices) {
            if (prices.empty()) return 0.0;
            std::sort(prices.begin(), prices.end());
            size_t mid = prices.size() / 2;
            return prices.size() % 2 == 0 ? 
                   (prices[mid - 1] + prices[mid]) / 2.0 : prices[mid];
        }
        
        static double standardDeviation(const std::vector<double>& prices) {
            double m = mean(prices);
            double sum = 0.0;
            for (double p : prices) sum += (p - m) * (p - m);
            return std::sqrt(sum / prices.size());
        }
        
        static double skewness(const std::vector<double>& prices) {
            double m = mean(prices);
            double sd = standardDeviation(prices);
            if (sd == 0) return 0.0;
            double sum = 0.0;
            for (double p : prices) sum += std::pow((p - m) / sd, 3);
            return sum / prices.size();
        }
    };
    
    // Optimization: Gradient descent for game recommendation scoring
    class RecommendationOptimizer {
    private:
        double learningRate;
        int maxIterations;
        
    public:
        RecommendationOptimizer(double lr = 0.01, int maxIter = 1000)
            : learningRate(lr), maxIterations(maxIter) {}
        
        std::vector<double> optimizeWeights(const std::vector<GameVector>& games,
                                           const std::vector<double>& targetScores) {
            size_t numFeatures = games[0].features.size();
            std::vector<double> weights(numFeatures, 1.0 / numFeatures);
            
            for (int iter = 0; iter < maxIterations; ++iter) {
                std::vector<double> gradient(numFeatures, 0.0);
                double totalError = 0.0;
                
                for (size_t i = 0; i < games.size(); ++i) {
                    double prediction = 0.0;
                    for (size_t j = 0; j < numFeatures; ++j) {
                        prediction += weights[j] * games[i].features[j];
                    }
                    
                    double error = prediction - targetScores[i];
                    totalError += error * error;
                    
                    for (size_t j = 0; j < numFeatures; ++j) {
                        gradient[j] += error * games[i].features[j];
                    }
                }
                
                if (totalError < 1e-6) break;
                
                for (size_t j = 0; j < numFeatures; ++j) {
                    weights[j] -= learningRate * gradient[j] / games.size();
                }
            }
            
            return weights;
        }
    };
    
    // Probability: Bayesian rating system
    class BayesianRating {
    public:
        static double wilsonScore(double positive, double total, double z = 1.96) {
            if (total == 0) return 0.0;
            double p = positive / total;
            double z2 = z * z;
            double denominator = 1 + z2 / total;
            double center = (p + z2 / (2 * total)) / denominator;
            double margin = z * std::sqrt((p * (1 - p) + z2 / (4 * total)) / total) / denominator;
            return center - margin;
        }
    };
}

//==============================================================================
// HTTP CLIENT FOR STEAM STORE CONNECTION
//==============================================================================

class SteamHTTPClient {
private:
    std::string baseUrl;
    std::string userAgent;
    
#ifdef _WIN32
    HINTERNET hSession;
    HINTERNET hConnect;
#endif
    
public:
    SteamHTTPClient(const std::string& url = "https://store.steampowered.com")
        : baseUrl(url), userAgent("SteamStoreConnector/1.0") {
#ifdef _WIN32
        hSession = WinHttpOpen(L"SteamStoreConnector/1.0",
                               WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                               WINHTTP_NO_PROXY_NAME,
                               WINHTTP_NO_PROXY_BYPASS, 0);
#endif
    }
    
    ~SteamHTTPClient() {
#ifdef _WIN32
        if (hConnect) WinHttpCloseHandle(hConnect);
        if (hSession) WinHttpCloseHandle(hSession);
#endif
    }
    
    std::string makeGETRequest(const std::string& endpoint) {
        std::string fullUrl = baseUrl + endpoint;
        std::string response;
        
#ifdef _WIN32
        // Parse URL
        std::wstring wUrl(fullUrl.begin(), fullUrl.end());
        URL_COMPONENTS urlComp = {0};
        urlComp.dwStructSize = sizeof(urlComp);
        
        wchar_t hostName[256] = {0};
        wchar_t urlPath[1024] = {0};
        urlComp.lpszHostName = hostName;
        urlComp.dwHostNameLength = 256;
        urlComp.lpszUrlPath = urlPath;
        urlComp.dwUrlPathLength = 1024;
        
        WinHttpCrackUrl(wUrl.c_str(), 0, 0, &urlComp);
        
        hConnect = WinHttpConnect(hSession, hostName, urlComp.nPort, 0);
        HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"GET", urlPath,
                                                 NULL, WINHTTP_NO_REFERER,
                                                 WINHTTP_DEFAULT_ACCEPT_TYPES,
                                                 WINHTTP_FLAG_SECURE);
        
        WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                          WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
        WinHttpReceiveResponse(hRequest, NULL);
        
        DWORD bytesRead;
        char buffer[4096];
        while (WinHttpReadData(hRequest, buffer, sizeof(buffer), &bytesRead)) {
            if (bytesRead == 0) break;
            response.append(buffer, bytesRead);
        }
        
        WinHttpCloseHandle(hRequest);
#else
        // libcurl implementation for non-Windows
        CURL* curl = curl_easy_init();
        if (curl) {
            curl_easy_setopt(curl, CURLOPT_URL, fullUrl.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
            curl_easy_setopt(curl, CURLOPT_USERAGENT, userAgent.c_str());
            curl_easy_perform(curl);
            curl_easy_cleanup(curl);
        }
#endif
        
        return response;
    }
    
private:
#ifndef _WIN32
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* output) {
        size_t totalSize = size * nmemb;
        output->append((char*)contents, totalSize);
        return totalSize;
    }
#endif
};

//==============================================================================
// STEAM STORE DATA PARSER
//==============================================================================

class SteamStoreParser {
public:
    struct GameInfo {
        std::string appId;
        std::string name;
        double price;
        double originalPrice;
        int discountPercent;
        std::vector<std::string> tags;
        std::string releaseDate;
        double reviewScore;
        int totalReviews;
        std::string developer;
        std::string publisher;
        
        // Feature vector for mathematical analysis
        std::vector<double> toFeatureVector() const {
            return {
                price,
                originalPrice > 0 ? price / originalPrice : 1.0,
                static_cast<double>(discountPercent) / 100.0,
                reviewScore / 100.0,
                std::log1p(totalReviews) / 15.0, // Normalized log scale
                static_cast<double>(tags.size()) / 20.0
            };
        }
    };
    
    std::vector<GameInfo> parseSearchResults(const std::string& html) {
        std::vector<GameInfo> games;
        
        // Parse JSON from Steam's dynamic content
        try {
            // Extract JSON data from script tags
            std::regex jsonPattern("data-store-tmpl=\"([^\"]+)\"");
            std::smatch matches;
            
            if (std::regex_search(html, matches, jsonPattern)) {
                json data = json::parse(matches[1].str());
                // Process game data...
            }
        } catch (const std::exception& e) {
            std::cerr << "JSON parsing error: " << e.what() << std::endl;
        }
        
        // Parse HTML for game information
        std::regex gamePattern("<a[^>]*class=\"search_result_row\"[^>]*data-ds-appid=\"(\\d+)\"[^>]*>");
        std::regex titlePattern("<span class=\"title\">([^<]+)</span>");
        std::regex pricePattern("(\\d+\\.?\\d*)");
        std::regex reviewPattern("data-tooltip-html=\"(\\d+)%");
        
        auto begin = std::sregex_iterator(html.begin(), html.end(), gamePattern);
        auto end = std::sregex_iterator();
        
        for (auto it = begin; it != end; ++it) {
            GameInfo game;
            game.appId = (*it)[1].str();
            
            // Extract more details from the game block
            std::string gameBlock = it->str();
            
            std::smatch titleMatch;
            if (std::regex_search(gameBlock, titleMatch, titlePattern)) {
                game.name = titleMatch[1].str();
            }
            
            std::smatch reviewMatch;
            if (std::regex_search(gameBlock, reviewMatch, reviewPattern)) {
                game.reviewScore = std::stod(reviewMatch[1].str());
            }
            
            games.push_back(game);
        }
        
        return games;
    }
    
    std::vector<GameInfo> parseAppDetails(const std::string& jsonResponse) {
        std::vector<GameInfo> games;
        
        try {
            json data = json::parse(jsonResponse);
            
            for (auto& [appId, appData] : data.items()) {
                if (appData["success"].get<bool>()) {
                    GameInfo game;
                    game.appId = appId;
                    game.name = appData["data"]["name"].get<std::string>();
                    game.developer = appData["data"]["developers"][0].get<std::string>();
                    game.publisher = appData["data"]["publishers"][0].get<std::string>();
                    
                    if (appData["data"].contains("price_overview")) {
                        game.price = appData["data"]["price_overview"]["final"].get<double>() / 100.0;
                        game.originalPrice = appData["data"]["price_overview"]["initial"].get<double>() / 100.0;
                        game.discountPercent = appData["data"]["price_overview"]["discount_percent"].get<int>();
                    }
                    
                    games.push_back(game);
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "JSON parsing error: " << e.what() << std::endl;
        }
        
        return games;
    }
};

//==============================================================================
// STEAM STORE CONNECTOR - MAIN CLASS
//==============================================================================

class SteamStoreConnector {
private:
    SteamHTTPClient httpClient;
    SteamStoreParser parser;
    std::vector<SteamStoreParser::GameInfo> cachedGames;
    
public:
    SteamStoreConnector() : httpClient("https://store.steampowered.com") {}
    
    // Search for games
    std::vector<SteamStoreParser::GameInfo> searchGames(const std::string& query) {
        std::string endpoint = "/search/?term=" + urlEncode(query);
        std::string response = httpClient.makeGETRequest(endpoint);
        return parser.parseSearchResults(response);
    }
    
    // Get featured games
    std::vector<SteamStoreParser::GameInfo> getFeaturedGames() {
        std::string endpoint = "/";
        std::string response = httpClient.makeGETRequest(endpoint);
        // Parse featured games from homepage
        return parser.parseSearchResults(response);
    }
    
    // Get game details via Steam API
    std::vector<SteamStoreParser::GameInfo> getAppDetails(const std::vector<std::string>& appIds) {
        std::string appList;
        for (size_t i = 0; i < appIds.size(); ++i) {
            if (i > 0) appList += ",";
            appList += appIds[i];
        }
        
        std::string endpoint = "/api/appdetails?appids=" + appList;
        std::string response = httpClient.makeGETRequest(endpoint);
        return parser.parseAppDetails(response);
    }
    
    // Mathematical analysis of game data
    void analyzeGames(const std::vector<SteamStoreParser::GameInfo>& games) {
        std::cout << "\n=== Steam Store Mathematical Analysis ===" << std::endl;
        
        // Extract price data
        std::vector<double> prices;
        for (const auto& game : games) {
            if (game.price > 0) prices.push_back(game.price);
        }
        
        // Price statistics
        auto stats = SteamMath::PriceStatistics();
        std::cout << "\nPrice Analysis:" << std::endl;
        std::cout << "  Mean: $" << std::fixed << std::setprecision(2) << stats.mean(prices) << std::endl;
        std::cout << "  Median: $" << stats.median(prices) << std::endl;
        std::cout << "  Std Dev: $" << stats.standardDeviation(prices) << std::endl;
        std::cout << "  Skewness: " << stats.skewness(prices) << std::endl;
        
        // Create feature vectors for games
        std::vector<SteamMath::GameVector> gameVectors;
        for (const auto& game : games) {
            gameVectors.emplace_back(game.name, game.toFeatureVector());
        }
        
        // Find similar games using cosine similarity
        if (gameVectors.size() >= 2) {
            std::cout << "\nGame Similarity Matrix (Cosine):" << std::endl;
            for (size_t i = 0; i < std::min(gameVectors.size(), size_t(3)); ++i) {
                std::cout << "  " << gameVectors[i].gameName << ":" << std::endl;
                for (size_t j = i + 1; j < std::min(gameVectors.size(), size_t(5)); ++j) {
                    double similarity = gameVectors[i].cosineSimilarity(gameVectors[j]);
                    std::cout << "    -> " << gameVectors[j].gameName 
                             << ": " << std::fixed << std::setprecision(3) << similarity << std::endl;
                }
            }
        }
        
        // Bayesian rating analysis
        std::cout << "\nBayesian Rating Analysis:" << std::endl;
        for (const auto& game : games) {
            if (game.totalReviews > 0) {
                double positiveReviews = game.reviewScore * game.totalReviews / 100.0;
                double wilsonScore = SteamMath::BayesianRating::wilsonScore(
                    positiveReviews, game.totalReviews);
                std::cout << "  " << game.name << ": " 
                         << std::fixed << std::setprecision(3) << wilsonScore << std::endl;
            }
        }
    }
    
    // Optimize game recommendations
    std::vector<SteamStoreParser::GameInfo> getOptimizedRecommendations(
        const std::vector<SteamStoreParser::GameInfo>& games,
        const std::vector<double>& userPreferences) {
        
        std::vector<SteamMath::GameVector> gameVectors;
        for (const auto& game : games) {
            gameVectors.emplace_back(game.name, game.toFeatureVector());
        }
        
        // Use gradient descent to optimize recommendation weights
        SteamMath::RecommendationOptimizer optimizer(0.01, 500);
        std::vector<double> weights = optimizer.optimizeWeights(gameVectors, userPreferences);
        
        // Score all games with optimized weights
        std::vector<std::pair<double, size_t>> scored;
        for (size_t i = 0; i < games.size(); ++i) {
            double score = 0.0;
            auto features = games[i].toFeatureVector();
            for (size_t j = 0; j < weights.size(); ++j) {
                score += weights[j] * features[j];
            }
            scored.emplace_back(score, i);
        }
        
        // Sort by score descending
        std::sort(scored.begin(), scored.end(), std::greater<>());
        
        // Return top recommendations
        std::vector<SteamStoreParser::GameInfo> recommendations;
        for (size_t i = 0; i < std::min(scored.size(), size_t(10)); ++i) {
            recommendations.push_back(games[scored[i].second]);
        }
        
        return recommendations;
    }
    
private:
    std::string urlEncode(const std::string& str) {
        std::ostringstream escaped;
        escaped.fill('0');
        escaped << std::hex;
        
        for (char c : str) {
            if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
                escaped << c;
            } else {
                escaped << '%' << std::setw(2) << int(static_cast<unsigned char>(c));
            }
        }
        
        return escaped.str();
    }
};

//==============================================================================
// MAIN APPLICATION
//==============================================================================

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "  Steam Store Connector - C++ Edition" << std::endl;
    std::cout << "  Mathematical Analysis Engine" << std::endl;
    std::cout << "========================================" << std::endl;
    
    SteamStoreConnector connector;
    
    // Connect to Steam store
    std::cout << "\n[1] Connecting to store.steampowered.com..." << std::endl;
    auto featuredGames = connector.getFeaturedGames();
    std::cout << "  Found " << featuredGames.size() << " featured games" << std::endl;
    
    // Search for games
    std::cout << "\n[2] Searching for games..." << std::endl;
    auto searchResults = connector.searchGames("rpg");
    std::cout << "  Found " << searchResults.size() << " RPG games" << std::endl;
    
    // Get app details
    std::cout << "\n[3] Fetching game details via Steam API..." << std::endl;
    std::vector<std::string> appIds = {"730", "570", "440"}; // CS:GO, Dota 2, TF2
    auto appDetails = connector.getAppDetails(appIds);
    std::cout << "  Retrieved details for " << appDetails.size() << " games" << std::endl;
    
    // Perform mathematical analysis
    std::cout << "\n[4] Performing mathematical analysis..." << std::endl;
    connector.analyzeGames(appDetails);
    
    // Get optimized recommendations
    std::cout << "\n[5] Generating optimized recommendations..." << std::endl;
    std::vector<double> userPrefs = {0.3, 0.8, 0.5, 0.9, 0.4, 0.6};
    auto recommendations = connector.getOptimizedRecommendations(appDetails, userPrefs);
    
    std::cout << "\nTop Recommendations:" << std::endl;
    for (size_t i = 0; i < recommendations.size(); ++i) {
        std::cout << "  " << (i + 1) << ". " << recommendations[i].name 
                  << " ($" << std::fixed << std::setprecision(2) << recommendations[i].price << ")" << std::endl;
    }
    
    std::cout << "\n[Complete] Steam Store connection and analysis finished." << std::endl;
    return 0;
}