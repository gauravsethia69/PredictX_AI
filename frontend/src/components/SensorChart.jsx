import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

export default function SensorChart({ data = [] }) {
  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid stroke="#242a33" strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            stroke="#6f7782"
            tick={{ fill: "#7f8792", fontSize: 11 }}
          />
          <YAxis
            stroke="#6f7782"
            tick={{ fill: "#7f8792", fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{
              background: "#12161c",
              border: "1px solid #2a3039",
              color: "#fff"
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line
            type="monotone"
            dataKey="temperature"
            name="Temperature °C"
            stroke="#ff7a00"
            dot={data.length <= 8 ? { r: 3 } : false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="vibration"
            name="Vibration"
            stroke="#ff4d55"
            dot={data.length <= 8 ? { r: 3 } : false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="current"
            name="Current A"
            stroke="#35d07f"
            dot={data.length <= 8 ? { r: 3 } : false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="sound"
            name="Sound dB"
            stroke="#45a8ff"
            dot={data.length <= 8 ? { r: 3 } : false}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
