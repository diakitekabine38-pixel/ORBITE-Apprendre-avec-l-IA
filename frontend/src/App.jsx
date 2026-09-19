import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Private from "./components/Private";
import Home from "./pages/Home";
import Catalog from "./pages/Catalog";
import CourseDetail from "./pages/CourseDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Learn from "./pages/Learn";
import Chat from "./pages/Chat";
import Certificates from "./pages/Certificates";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalogue" element={<Catalog />} />
          <Route path="/formations/:slug" element={<CourseDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/inscription" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <Private>
                <Dashboard />
              </Private>
            }
          />
          <Route
            path="/apprentissage/:slug"
            element={
              <Private>
                <Learn />
              </Private>
            }
          />
          <Route
            path="/chat"
            element={
              <Private>
                <Chat />
              </Private>
            }
          />
          <Route
            path="/certificats"
            element={
              <Private>
                <Certificates />
              </Private>
            }
          />
          <Route
            path="/panier"
            element={
              <Private>
                <Cart />
              </Private>
            }
          />
          <Route
            path="/paiement"
            element={
              <Private>
                <Checkout />
              </Private>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}