import "./globals.css";

export const metadata = {
  title: "Ride-Hailing & Cab Platform",
  description: "FastAPI + Next.js + Socket.IO + PostGIS Ride Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
