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

const API_URL = "https://organic-space-system-69r4gq7p7449c4j56-8000.app.github.dev";

export default function Home() {
  const [prices, setPrices] = useState<Price[]>([]);
  const [history, setHistory] = useState<Price[]>([]);
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [loading, setLoading] = useState(true);

  async function fetchPrices() {
    try {
      const res = await fetch(`${API_URL}/prices`);
      const data = await res.json();

      if (Array.isArray(data)) {
        setPrices(data);
      } else {
        console.error("Prices API did not return array:", data);
        setPrices([]);
      }
    } catch (error) {
      console.error("Error fetching prices:", error);
      setPrices([]);
    }
  }

  async function fetchHistory(symbol: string) {
    try {
      const res = await fetch(`${API_URL}/history/${symbol}`);
      const data = await res.json();

      if (Array.isArray(data)) {
        setHistory(data);
      } else {
        console.error("History API did not return array:", data);
        setHistory([]);
      }
    } catch (error) {
      console.error("Error fetching history:", error);
      setHistory([]);
    }
  }

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      await fetchPrices();
      await fetchHistory(selectedCoin);
      setLoading(false);
    }

    loadData();

    const interval = setInterval(() => {
      fetchPrices();
      fetchHistory(selectedCoin);
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedCoin]);

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <h1 className="text-4xl font-bold mb-2">MarketMind AI</h1>

      <p className="text-gray-400 mb-8">
        Real-time crypto market intelligence dashboard
      </p>

      {loading && (
        <p className="text-yellow-400 mb-4">
          Loading market data...
        </p>
      )}

      {!loading && prices.length === 0 && (
        <div className="rounded-xl border border-red-800 bg-red-950 p-4 mb-6">
          <p className="text-red-300 font-semibold">
            No price data found.
          </p>
          <p className="text-red-200 text-sm mt-1">
            Check that your backend is running and API_URL is correct.
          </p>
        </div>
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
    </main>
  );
}