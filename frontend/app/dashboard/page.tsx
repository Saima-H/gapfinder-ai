"use client";

import { useEffect, useState } from "react";
import { createClient } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function Dashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true); // <-- Added loading state

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/"); // Kick to login
      } else {
        setLoading(false); // Only show the dashboard if logged in
      }
    };
    checkAuth();
  }, [router]);

  // While checking auth, show a loading screen
  if (loading) {
    return <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold text-blue-400 mb-8">GapFinder AI Dashboard</h1>
      <div className="bg-gray-800 p-6 rounded-lg">
        <p className="text-gray-300">
          Welcome to GapFinder AI! The upload interface will be built here.
        </p>
      </div>
    </div>
  );
}