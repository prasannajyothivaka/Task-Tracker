import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useLocation } from "react-router-dom";
import { ssoLogin } from "../features/authSlice";
import { GOOGLE_CLIENT_ID, GSI_CLIENT_URL } from "../constants/globalConstants";

const GoogleSSO = () => {
  const [error, setError] = useState("");
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const { userInfo } = useSelector((state) => state.userLogin);
  const redirect = new URLSearchParams(location.search).get("redirect") || "/";

  useEffect(() => {
    const script = document.createElement("script");
    script.src = GSI_CLIENT_URL;
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

      setTimeout(() => {
        const buttonDiv = document.getElementById("google-btn");
        if (buttonDiv) {
          window.google.accounts.id.renderButton(buttonDiv, {
            theme: "filled_blue",
            size: "large",
            shape: "pill",
            text: "signin_with",
            width: "100%", // full width
          });
          setIsGoogleLoaded(true);
        }
      }, 100);
    }
  };

  const handleResponse = async (response) => {
    try {
      const payload = JSON.parse(atob(response.credential.split(".")[1]));
      const token = response.credential;

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
      <div className="bg-white p-6 rounded-2xl shadow-md w-full max-w-md text-center">
        <h2 className="text-xl font-semibold mb-4">Login with Google SSO</h2>
        {error && (
          <p className="bg-red-100 text-red-600 p-2 mb-3 rounded">{error}</p>
        )}

        {/* Full-width wrapper */}
        <div className="mt-4 w-full flex justify-center">
          <div
            id="google-btn"
            className={`transition-opacity duration-300 w-full ${
              isGoogleLoaded ? "opacity-100" : "opacity-0"
            }`}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default GoogleSSO;
