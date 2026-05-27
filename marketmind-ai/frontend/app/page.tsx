"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Price = {
  symbol: string;
  price_usd: number;
  change_24h: number;
  volume_24h: number;
  market_cap: number;
  timestamp: string;
};

type NewsArticle = {
  title: string;
  source: string;
  url: string;
  sentiment: string;
  sentiment_score: number;
  published_at: string;
  created_at?: string;
};

type MarketSummary = {
  overall_sentiment: string;
  summary: string;
  positive_news: number;
  negative_news: number;
  neutral_news: number;
  total_articles: number;
};

const API_URL =
  "https://organic-space-system-69r4gq7p7449c4j56-8000.app.github.dev";

export default function Home() {
  const [prices, setPrices] = useState<Price[]>([]);
  const [history, setHistory] = useState<Price[]>([]);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [summary, setSummary] = useState<MarketSummary | null>(null);
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [loading, setLoading] = useState(true);

  async function fetchPrices() {
    try {
      const res = await fetch(`${API_URL}/prices`);
      const data = await res.json();
      setPrices(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching prices:", error);
      setPrices([]);
    }
  }

  async function fetchHistory(symbol: string) {
    try {
      const res = await fetch(`${API_URL}/history/${symbol}`);
      const data = await res.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching history:", error);
      setHistory([]);
    }
  }

  async function fetchNews() {
    try {
      const res = await fetch(`${API_URL}/news`);
      const data = await res.json();
      setNews(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching news:", error);
      setNews([]);
    }
  }

  async function fetchSummary() {
    try {
      const res = await fetch(`${API_URL}/summary`);
      const data = await res.json();
      setSummary(data);
    } catch (error) {
      console.error("Error fetching summary:", error);
      setSummary(null);
    }
  }

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      await fetchPrices();
      await fetchHistory(selectedCoin);
      await fetchNews();
      await fetchSummary();
      setLoading(false);
    }

    loadData();

    const interval = setInterval(() => {
      fetchPrices();
      fetchHistory(selectedCoin);
      fetchNews();
      fetchSummary();
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedCoin]);

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <h1 className="text-4xl font-bold mb-2">MarketMind AI</h1>

      <p className="text-gray-400 mb-8">
        Real-time crypto market intelligence dashboard
      </p>

      {loading && <p className="text-yellow-400 mb-4">Loading market data...</p>}

      {summary && (
        <section className="mb-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">AI Market Summary</h2>

            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold ${
                summary.overall_sentiment === "Bullish"
                  ? "bg-green-900 text-green-300"
                  : summary.overall_sentiment === "Bearish"
                  ? "bg-red-900 text-red-300"
                  : "bg-zinc-800 text-zinc-300"
              }`}
            >
              {summary.overall_sentiment}
            </span>
          </div>

          <p className="text-gray-300 leading-7 mb-6">{summary.summary}</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-xl bg-zinc-900 p-4">
              <p className="text-sm text-gray-400">Positive</p>
              <p className="text-2xl font-bold text-green-400">
                {summary.positive_news}
              </p>
            </div>

            <div className="rounded-xl bg-zinc-900 p-4">
              <p className="text-sm text-gray-400">Negative</p>
              <p className="text-2xl font-bold text-red-400">
                {summary.negative_news}
              </p>
            </div>

            <div className="rounded-xl bg-zinc-900 p-4">
              <p className="text-sm text-gray-400">Neutral</p>
              <p className="text-2xl font-bold text-gray-300">
                {summary.neutral_news}
              </p>
            </div>

            <div className="rounded-xl bg-zinc-900 p-4">
              <p className="text-sm text-gray-400">Articles</p>
              <p className="text-2xl font-bold">{summary.total_articles}</p>
            </div>
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {prices.map((coin) => (
          <button
            key={`${coin.symbol}-${coin.timestamp}`}
            onClick={() => setSelectedCoin(coin.symbol)}
            className={`rounded-2xl border p-4 text-left transition ${
              selectedCoin === coin.symbol
                ? "border-green-400 bg-zinc-900"
                : "border-zinc-800 bg-zinc-950 hover:bg-zinc-900"
            }`}
          >
            <h2 className="text-xl font-semibold">{coin.symbol}</h2>

            <p className="text-2xl font-bold mt-2">
              ${coin.price_usd?.toLocaleString() ?? "N/A"}
            </p>

            <p
              className={`mt-2 ${
                coin.change_24h >= 0 ? "text-green-400" : "text-red-400"
              }`}
            >
              {coin.change_24h !== undefined && coin.change_24h !== null
                ? `${coin.change_24h.toFixed(2)}%`
                : "N/A"}
            </p>

            <p className="text-xs text-gray-500 mt-2">
              Vol: ${coin.volume_24h?.toLocaleString() ?? "N/A"}
            </p>
          </button>
        ))}
      </div>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
        <h2 className="text-2xl font-bold mb-4">
          {selectedCoin} Price History
        </h2>

        {history.length === 0 ? (
          <p className="text-gray-400">
            No history data yet. Wait for backend ingestion to store records.
          </p>
        ) : (
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <XAxis dataKey="timestamp" hide />
                <YAxis domain={["auto", "auto"]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="price_usd"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <section className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
        <h2 className="text-2xl font-bold mb-6">Latest Crypto News</h2>

        {news.length === 0 ? (
          <p className="text-gray-400">
            No news data yet. Check backend `/news` endpoint.
          </p>
        ) : (
          <div className="space-y-4">
            {news.map((article, index) => (
              <a
                key={`${article.url}-${index}`}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded-xl border border-zinc-800 p-4 hover:bg-zinc-900 transition"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-400">{article.source}</p>

                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      article.sentiment === "positive"
                        ? "bg-green-900 text-green-300"
                        : article.sentiment === "negative"
                        ? "bg-red-900 text-red-300"
                        : "bg-zinc-800 text-zinc-300"
                    }`}
                  >
                    {article.sentiment}
                  </span>
                </div>

                <h3 className="font-semibold text-lg">{article.title}</h3>

                <p className="text-xs text-gray-500 mt-2">
                  Sentiment score: {article.sentiment_score}
                </p>
              </a>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}