import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate,useLocation } from "react-router-dom";
import { ssoLogin } from "../features/authSlice"; // <-- sso thunk

const GoogleSSO = () => {
  const [error, setError] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const { userInfo } = useSelector((state) => state.userLogin); // read userInfo from state
  const redirect = new URLSearchParams(location.search).get("redirect") || "/";


  const GOOGLE_CLIENT_ID =
    "313608268610-dbo3eur26g6g2576rkl0apbgm43roi8h.apps.googleusercontent.com";

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = initGoogle;
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) document.body.removeChild(script);
    };
  }, []);

  useEffect(() => {
    // redirect if login successful
    if (userInfo) {
      navigate(redirect);
    }
  }, [userInfo, navigate, redirect]);

  const initGoogle = () => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleResponse,
      });

      window.google.accounts.id.renderButton(
        document.getElementById("google-btn"),
        { theme: "filled_blue", size: "large", shape: "pill", text: "signin" }
      );
    }
  };

  const handleResponse = async (response) => {
    try {
      const payload = JSON.parse(atob(response.credential.split(".")[1]));
      const token = response.credential;

      // Dispatch ssoLogin thunk with token
      await dispatch(ssoLogin({ token }));
      setError("");
      console.log("✅ Logged in via SSO:", payload.email);
    } catch (err) {
      console.error("Google SSO error:", err);
      setError("Login failed. Try again.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="bg-white p-6 rounded-2xl shadow-md w-96 text-center">
        <h2 className="text-xl font-semibold mb-4">Login with Google SSO</h2>
        {error && (
          <p className="bg-red-100 text-red-600 p-2 mb-3 rounded">{error}</p>
        )}
        <div id="google-btn" className="flex justify-center"></div>
      </div>
    </div>
  );
};

export default GoogleSSO;
