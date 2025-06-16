// Dashboard.jsx
import { useEffect, useState } from "react";

export default function Dashboard() {
    const [orders, setOrders]     = useState([]);
    const [trades, setTrades]     = useState([]);
    const [positions, setPositions] = useState([]);

    const fetchAPI = async (endpoint) => {
        const res = await fetch(`/api/${endpoint}`);
        if (!res.ok) throw new Error(res.statusText);
        return res.json();
    };

    const refreshAll = async () => {
        const [o, t, p] = await Promise.all([
            fetchAPI("orders"),
            fetchAPI("trades?limit=50"),
            fetchAPI("positions"),
        ]);
        setOrders(o);
        setTrades(t);
        setPositions(p);
    };

    useEffect(() => {
        refreshAll();
        const id = setInterval(refreshAll, 5000);
        return () => clearInterval(id);
    }, []);

    const fmt = (n) => (n == null ? "—" : Number(n).toFixed(2));

    return (
        <div className="p-4 grid gap-6 lg:grid-cols-3">
            {/* Orders */}
            <div className="border rounded p-4">
                <h2 className="font-bold mb-2">Open Orders</h2>
                <table className="text-xs w-full">
                    <thead>
                    <tr>
                        <th>ID</th>
                        <th>Sym</th>
                        <th>Side</th>
                        <th>Qty</th>
                        <th>Rem</th>
                        <th>Px</th>
                    </tr>
                    </thead>
                    <tbody>
                    {orders.map(o => (
                        <tr key={o.id}>
                            <td>{o.id}</td>
                            <td>{o.symbol}</td>
                            <td className={o.side === "buy" ? "text-green-600" : "text-red-600"}>
                                {o.side}
                            </td>
                            <td>{o.quantity}</td>
                            <td>{o.remaining_qty}</td>
                            <td>{fmt(o.price)}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            {/* Trades */}
            <div className="border rounded p-4">
                <h2 className="font-bold mb-2">Recent Trades</h2>
                <table className="text-xs w-full">
                    <thead>
                    <tr>
                        <th>ID</th>
                        <th>Sym</th>
                        <th>Qty</th>
                        <th>Px</th>
                        <th>Time</th>
                    </tr>
                    </thead>
                    <tbody>
                    {trades.map(t => (
                        <tr key={t.id}>
                            <td>{t.id}</td>
                            <td>{t.symbol}</td>
                            <td>{t.quantity}</td>
                            <td>{fmt(t.price)}</td>
                            <td>{new Date(t.executed_at).toLocaleTimeString()}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            {/* Positions */}
            <div className="border rounded p-4">
                <h2 className="font-bold mb-2">Positions & P/L</h2>
                <table className="text-xs w-full">
                    <thead>
                    <tr>
                        <th>Sym</th>
                        <th>Qty</th>
                        <th>Avg Px</th>
                        <th>Last Px</th>
                        <th>P/L</th>
                    </tr>
                    </thead>
                    <tbody>
                    {positions.map(p => (
                        <tr key={`${p.firm_id}-${p.symbol}`}>
                            <td>{p.symbol}</td>
                            <td>{p.net_qty}</td>
                            <td>{fmt(p.avg_price)}</td>
                            <td>{fmt(p.last_price)}</td>
                            <td className={p.pnl >= 0 ? "text-green-600" : "text-red-600"}>
                                {fmt(p.pnl)}
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}