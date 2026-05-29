import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Dumbbell,
  Edit3,
  Gauge,
  HeartPulse,
  Bot,
  LogOut,
  MessageCircle,
  Moon,
  Plus,
  Salad,
  Search,
  Trash2,
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL;
const today = new Date().toISOString().slice(0, 10);

function App() {
  const [token, setToken] = useState(localStorage.getItem("healthToken") || "");
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [message, setMessage] = useState("");

  const authedFetch = useMemo(() => {
    return (path, options = {}) =>
      fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          ...(options.headers || {}),
        },
      });
  }, [token]);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }

    authedFetch("/me")
      .then((response) => {
        if (!response.ok) throw new Error("Session expired");
        return response.json();
      })
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("healthToken");
        setToken("");
      });
  }, [authedFetch, token]);

  function saveToken(nextToken) {
    localStorage.setItem("healthToken", nextToken);
    setToken(nextToken);
  }

  function logout() {
    localStorage.removeItem("healthToken");
    setToken("");
    setUser(null);
  }

  if (!token || !user) {
    return <AuthScreen onLogin={saveToken} message={message} setMessage={setMessage} />;
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <HeartPulse size={25} />
          </div>
          <div>
            <strong>Health Tracker</strong>
            <span>{user.name}</span>
          </div>
        </div>

        <nav>
          <TabButton active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")}>
            <HeartPulse size={18} /> Dashboard
          </TabButton>
          <TabButton active={activeTab === "goals"} onClick={() => setActiveTab("goals")}>
            <Gauge size={18} /> Goals
          </TabButton>
          <TabButton active={activeTab === "meals"} onClick={() => setActiveTab("meals")}>
            <Salad size={18} /> Meals
          </TabButton>
          <TabButton active={activeTab === "sleep"} onClick={() => setActiveTab("sleep")}>
            <Moon size={18} /> Sleep
          </TabButton>
          <TabButton active={activeTab === "workouts"} onClick={() => setActiveTab("workouts")}>
            <Dumbbell size={18} /> Workouts
          </TabButton>
          <TabButton active={activeTab === "social"} onClick={() => setActiveTab("social")}>
            <MessageCircle size={18} /> Community
          </TabButton>
          <TabButton active={activeTab === "coach"} onClick={() => setActiveTab("coach")}>
            <Bot size={18} /> AI Coach
          </TabButton>
        </nav>

        <button className="ghost-button" onClick={logout}>
          <LogOut size={18} /> Logout
        </button>
      </aside>

      <section className="workspace">
        {activeTab === "dashboard" && <Dashboard fetcher={authedFetch} />}
        {activeTab === "goals" && <Goals fetcher={authedFetch} />}
        {activeTab === "meals" && <Meals fetcher={authedFetch} />}
        {activeTab === "sleep" && <Sleep fetcher={authedFetch} />}
        {activeTab === "workouts" && <Workouts fetcher={authedFetch} />}
        {activeTab === "social" && <Community fetcher={authedFetch} />}
        {activeTab === "coach" && <Coach fetcher={authedFetch} />}
      </section>
    </main>
  );
}

function AuthScreen({ onLogin, message, setMessage }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    name: "",
    email: "aadish102005@gmail.com",
    password: "Aadish917",
  });

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setMessage("");

    try {
      if (mode === "register") {
        const query = new URLSearchParams(form);
        const response = await fetch(`${API_URL}/register?${query}`, { method: "POST" });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Registration failed");
        setMessage("Account created. Logging you in now.");
      }

      const loginQuery = new URLSearchParams({
        email: form.email,
        password: form.password,
      });
      const loginResponse = await fetch(`${API_URL}/login?${loginQuery}`, { method: "POST" });
      const loginData = await loginResponse.json();

      if (!loginResponse.ok) throw new Error(loginData.detail || "Login failed");
      onLogin(loginData.access_token);
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-visual">
        <div className="pulse-badge">
          <HeartPulse size={80} />
        </div>
        <h1>Health Tracker</h1>
        <p>Track food, sleep, workouts, progress, and community motivation from one clean dashboard.</p>
      </section>

      <form className="auth-panel" onSubmit={submit}>
        <div className="segment-control">
          <button type="button" className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")}>
            Login
          </button>
          <button type="button" className={mode === "register" ? "selected" : ""} onClick={() => setMode("register")}>
            Register
          </button>
        </div>

        {mode === "register" && (
          <label>
            Name
            <input value={form.name} onChange={(event) => update("name", event.target.value)} required />
          </label>
        )}

        <label>
          Email
          <input type="email" value={form.email} onChange={(event) => update("email", event.target.value)} required />
        </label>

        <label>
          Password
          <input type="password" value={form.password} onChange={(event) => update("password", event.target.value)} required />
        </label>

        {message && <p className="form-message">{message}</p>}

        <button className="primary-button" type="submit">
          {mode === "login" ? "Login" : "Create Account"}
        </button>
      </form>
    </main>
  );
}

function TabButton({ active, children, onClick }) {
  return (
    <button className={active ? "nav-button active" : "nav-button"} onClick={onClick}>
      {children}
    </button>
  );
}

function Dashboard({ fetcher }) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    fetcher("/dashboard")
      .then((response) => response.json())
      .then(setDashboard);
  }, [fetcher]);

  if (!dashboard) return <PageTitle title="Dashboard" subtitle="Loading your health summary..." />;

  const totals = dashboard.totals;
  const goals = dashboard.goals;
  const todayTotals = dashboard.today;

  return (
    <>
      <PageTitle title="Dashboard" subtitle="Your latest food, sleep, and training picture." />
      <div className="stats-grid">
        <Stat label="Calories eaten" value={totals.calories} tone="green" />
        <Stat label="Protein" value={`${totals.protein}g`} tone="blue" />
        <Stat label="Carbs / Fat" value={`${totals.carbs}g / ${totals.fat}g`} tone="purple" />
        <Stat label="Workout minutes" value={totals.minutes} tone="red" />
        <Stat label="Avg sleep" value={`${totals.average_sleep}h`} tone="purple" />
      </div>

      {goals && (
        <section className="goal-progress-grid">
          <GoalProgress label="Calories today" value={todayTotals.calories} goal={goals.calorie_goal} unit="cal" />
          <GoalProgress label="Protein today" value={todayTotals.protein} goal={goals.protein_goal} unit="g" />
          <GoalProgress label="Carbs today" value={todayTotals.carbs} goal={goals.carbs_goal} unit="g" />
          <GoalProgress label="Fat today" value={todayTotals.fat} goal={goals.fat_goal} unit="g" />
        </section>
      )}

      <section className="dashboard-grid">
        <RecentList title="Recent meals" items={dashboard.recent.meals} fields={["name", "quantity_grams", "calories", "entry_date"]} />
        <RecentList title="Recent sleep" items={dashboard.recent.sleep} fields={["hours", "quality", "entry_date"]} />
        <RecentList title="Recent workouts" items={dashboard.recent.workouts} fields={["activity", "duration", "entry_date"]} />
      </section>
    </>
  );
}

function Goals({ fetcher }) {
  const [form, setForm] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetcher("/goals")
      .then((response) => response.json())
      .then(setForm);
  }, [fetcher]);

  if (!form) return <PageTitle title="Goals" subtitle="Loading your calorie and macro targets..." />;

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function calculate() {
    const response = await fetcher("/maintenance-calories", {
      method: "POST",
      body: JSON.stringify(form),
    });
    const data = await response.json();

    if (response.ok) {
      setForm((current) => ({
        ...current,
        maintenance_calories: data.maintenance_calories,
        calorie_goal: data.maintenance_calories,
      }));
      setMessage("Maintenance calories calculated. Adjust the daily target if your goal is loss or gain.");
    }
  }

  async function save(event) {
    event.preventDefault();
    const response = await fetcher("/goals", {
      method: "PUT",
      body: JSON.stringify(form),
    });
    const data = await response.json();

    if (response.ok) {
      setForm(data);
      setMessage("Goals saved.");
    }
  }

  return (
    <>
      <PageTitle title="Goals" subtitle="Calculate maintenance calories and set daily macro targets." />
      <form className="goals-form" onSubmit={save}>
        <label>
          Age
          <input type="number" value={form.age} onChange={(event) => update("age", Number(event.target.value))} />
        </label>
        <label>
          Sex
          <select value={form.sex} onChange={(event) => update("sex", event.target.value)}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </label>
        <label>
          Height (cm)
          <input type="number" value={form.height_cm} onChange={(event) => update("height_cm", Number(event.target.value))} />
        </label>
        <label>
          Weight (kg)
          <input type="number" value={form.weight_kg} onChange={(event) => update("weight_kg", Number(event.target.value))} />
        </label>
        <label>
          Activity
          <select value={form.activity_level} onChange={(event) => update("activity_level", event.target.value)}>
            <option value="sedentary">Sedentary</option>
            <option value="light">Light</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
            <option value="athlete">Athlete</option>
          </select>
        </label>
        <label>
          Goal
          <select value={form.goal_type} onChange={(event) => update("goal_type", event.target.value)}>
            <option value="lose">Fat loss</option>
            <option value="maintain">Maintain</option>
            <option value="gain">Muscle gain</option>
          </select>
        </label>
        <label>
          Maintenance calories
          <input type="number" value={form.maintenance_calories} onChange={(event) => update("maintenance_calories", Number(event.target.value))} />
        </label>
        <label>
          Daily calorie goal
          <input type="number" value={form.calorie_goal} onChange={(event) => update("calorie_goal", Number(event.target.value))} />
        </label>
        <label>
          Protein goal (g)
          <input type="number" value={form.protein_goal} onChange={(event) => update("protein_goal", Number(event.target.value))} />
        </label>
        <label>
          Carbs goal (g)
          <input type="number" value={form.carbs_goal} onChange={(event) => update("carbs_goal", Number(event.target.value))} />
        </label>
        <label>
          Fat goal (g)
          <input type="number" value={form.fat_goal} onChange={(event) => update("fat_goal", Number(event.target.value))} />
        </label>

        <button className="secondary-button compact" type="button" onClick={calculate}>
          <Gauge size={18} /> Calculate
        </button>
        <button className="primary-button compact" type="submit">Save goals</button>
      </form>
      {message && <p className="form-message">{message}</p>}
    </>
  );
}

function Meals({ fetcher }) {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    name: "",
    meal_type: "Breakfast",
    quantity_grams: 100,
    calories: 400,
    protein: 20,
    carbs: 45,
    fat: 12,
    entry_date: today,
  });

  return (
    <TrackerPage
      title="Meal Tracking"
      subtitle="Search internet nutrition data, edit the macros, then save."
      fetcher={fetcher}
      path="/meals"
      lookupType="food"
      items={items}
      setItems={setItems}
      form={form}
      setForm={setForm}
      fields={[
        ["name", "Food name", "text"],
        ["meal_type", "Meal type", "select", ["Breakfast", "Lunch", "Dinner", "Snack"]],
        ["quantity_grams", "Food weight (g)", "number"],
        ["calories", "Calories", "number"],
        ["protein", "Protein (g)", "number"],
        ["carbs", "Carbs (g)", "number"],
        ["fat", "Fat (g)", "number"],
        ["entry_date", "Date", "date"],
      ]}
      display={["name", "meal_type", "quantity_grams", "calories", "protein", "carbs", "fat", "entry_date"]}
    />
  );
}

function Sleep({ fetcher }) {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ hours: 7.5, quality: "Good", entry_date: today });

  return (
    <TrackerPage
      title="Sleep Tracking"
      subtitle="Record rest duration and quality."
      fetcher={fetcher}
      path="/sleep"
      items={items}
      setItems={setItems}
      form={form}
      setForm={setForm}
      fields={[
        ["hours", "Hours", "number"],
        ["quality", "Quality", "select", ["Excellent", "Good", "Okay", "Poor"]],
        ["entry_date", "Date", "date"],
      ]}
      display={["hours", "quality", "entry_date"]}
    />
  );
}

function Workouts({ fetcher }) {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ activity: "", duration: 45, calories_burned: 250, entry_date: today });

  return (
    <TrackerPage
      title="Workout Tracking"
      subtitle="Estimate calories from activity data, edit the number, then save."
      fetcher={fetcher}
      path="/workouts"
      lookupType="workout"
      items={items}
      setItems={setItems}
      form={form}
      setForm={setForm}
      fields={[
        ["activity", "Activity", "text"],
        ["duration", "Duration (min)", "number"],
        ["calories_burned", "Calories burned", "number"],
        ["entry_date", "Date", "date"],
      ]}
      display={["activity", "duration", "calories_burned", "entry_date"]}
    />
  );
}

function TrackerPage({ title, subtitle, fetcher, path, lookupType, items, setItems, form, setForm, fields, display }) {
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState(null);
  const [lookupStatus, setLookupStatus] = useState("");
  const [foodResults, setFoodResults] = useState([]);
  const [weightKg, setWeightKg] = useState(70);

  function load() {
    fetcher(path)
      .then((response) => response.json())
      .then(setItems);
  }

  useEffect(load, [fetcher, path, setItems]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateEdit(field, value) {
    setEditForm((current) => ({ ...current, [field]: value }));
  }

  async function saveItem(event) {
    event.preventDefault();
    setSaving(true);

    const isEditing = editingId !== null;
    const payload = isEditing ? editForm : form;
    const response = await fetcher(isEditing ? `${path}/${editingId}` : path, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    setSaving(false);

    if (response.ok) {
      if (isEditing) {
        setItems((current) => current.map((item) => (item.id === editingId ? data : item)));
        setEditingId(null);
        setEditForm(null);
      } else {
        setItems((current) => [data, ...current]);
      }
    }
  }

  async function remove(id) {
    await fetcher(`${path}/${id}`, { method: "DELETE" });
    setItems((current) => current.filter((item) => item.id !== id));
  }

  async function lookupFood() {
    if (!form.name.trim()) {
      setLookupStatus("Enter a food name first.");
      return;
    }

    setLookupStatus("Searching nutrition database...");
    setFoodResults([]);

    try {
      const grams = form.quantity_grams || 100;
      const response = await fetcher(`/food-lookup?query=${encodeURIComponent(form.name)}&grams=${grams}`);
      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || "Food lookup failed");

      setFoodResults(data.results || []);
      setLookupStatus(data.results?.length ? "Choose a result below." : "No matching foods found.");
    } catch (error) {
      setLookupStatus(error.message);
    }
  }

  async function lookupWorkout() {
    if (!form.activity.trim()) {
      setLookupStatus("Enter an activity first.");
      return;
    }

    setLookupStatus("Estimating calories...");

    try {
      const query = new URLSearchParams({
        activity: form.activity,
        duration: form.duration,
        weight_kg: weightKg,
      });
      const response = await fetcher(`/workout-estimate?${query}`);
      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || "Workout estimate failed");

      setForm((current) => ({
        ...current,
        calories_burned: data.calories_burned,
      }));
      setLookupStatus(`Estimated ${data.calories_burned} calories from ${data.source}.`);
    } catch (error) {
      setLookupStatus(error.message);
    }
  }

  function applyFoodResult(result) {
      setForm((current) => ({
        ...current,
        name: result.name,
        quantity_grams: Number(result.serving_size.replace(" g", "")) || current.quantity_grams,
        calories: Math.round(result.calories),
      protein: result.protein,
      carbs: result.carbs,
      fat: result.fat,
    }));
    setFoodResults([]);
    setLookupStatus(`Applied macros from ${result.source}. You can edit them before saving.`);
  }

  function startEdit(item) {
    setEditingId(item.id);
    setEditForm(
      fields.reduce((current, [field]) => {
        current[field] = item[field];
        return current;
      }, {})
    );
  }

  function cancelEdit() {
    setEditingId(null);
    setEditForm(null);
  }

  const activeForm = editingId !== null ? editForm : form;
  const updateActiveForm = editingId !== null ? updateEdit : update;

  return (
    <>
      <PageTitle title={title} subtitle={subtitle} />
      {lookupType && (
        <section className="lookup-panel">
          {lookupType === "food" && (
            <>
              <button className="secondary-button" type="button" onClick={lookupFood}>
                <Search size={18} /> Get food macros
              </button>
              <span>Uses the entered food weight, local common-food macros, and Open Food Facts.</span>
            </>
          )}
          {lookupType === "workout" && (
            <>
              <label>
                Body weight (kg)
                <input
                  type="number"
                  value={weightKg}
                  onChange={(event) => setWeightKg(Number(event.target.value))}
                />
              </label>
              <button className="secondary-button" type="button" onClick={lookupWorkout}>
                <Search size={18} /> Estimate calories
              </button>
              <span>Uses activity MET estimates. Edit calories before saving.</span>
            </>
          )}
          {lookupStatus && <p>{lookupStatus}</p>}
          {foodResults.length > 0 && (
            <div className="lookup-results">
              {foodResults.map((result, index) => (
                <button type="button" key={`${result.name}-${index}`} onClick={() => applyFoodResult(result)}>
                  <strong>{result.name}</strong>
                  <span>{result.calories} cal | P {result.protein}g | C {result.carbs}g | F {result.fat}g</span>
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      <form className="entry-form" onSubmit={saveItem}>
        {fields.map(([field, label, type, options]) => (
          <label key={field}>
            {label}
            {type === "select" ? (
              <select value={activeForm[field]} onChange={(event) => updateActiveForm(field, event.target.value)}>
                {options.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            ) : (
              <input
                type={type}
                value={activeForm[field]}
                onChange={(event) => updateActiveForm(field, type === "number" ? Number(event.target.value) : event.target.value)}
                required
              />
            )}
          </label>
        ))}
        <button className="primary-button compact" type="submit" disabled={saving}>
          {editingId !== null ? <Edit3 size={18} /> : <Plus size={18} />}
          {editingId !== null ? "Save edits" : "Add"}
        </button>
        {editingId !== null && (
          <button className="secondary-button compact" type="button" onClick={cancelEdit}>
            Cancel
          </button>
        )}
      </form>

      <section className="data-list">
        {items.map((item) => (
          <article className="data-row" key={item.id}>
            <div>
              {display.map((field) => (
                <span key={field}>{String(item[field])}</span>
              ))}
            </div>
            <div className="row-actions">
              <button className="icon-button edit" onClick={() => startEdit(item)} title="Edit">
                <Edit3 size={18} />
              </button>
              <button className="icon-button" onClick={() => remove(item.id)} title="Delete">
                <Trash2 size={18} />
              </button>
            </div>
          </article>
        ))}
        {items.length === 0 && <p className="empty-state">No entries yet.</p>}
      </section>
    </>
  );
}

function Community({ fetcher }) {
  const [posts, setPosts] = useState([]);
  const [form, setForm] = useState({ content: "", mood: "Motivated" });

  function load() {
    fetcher("/posts")
      .then((response) => response.json())
      .then(setPosts);
  }

  useEffect(load, [fetcher]);

  async function submit(event) {
    event.preventDefault();
    const response = await fetcher("/posts", {
      method: "POST",
      body: JSON.stringify(form),
    });
    const data = await response.json();
    if (response.ok) {
      setPosts((current) => [data, ...current]);
      setForm({ content: "", mood: "Motivated" });
    }
  }

  async function like(id) {
    const response = await fetcher(`/posts/${id}/like`, { method: "POST" });
    const data = await response.json();
    if (response.ok) {
      setPosts((current) => current.map((post) => (post.id === id ? data : post)));
    }
  }

  return (
    <>
      <PageTitle title="Community" subtitle="Share progress and support each other." />
      <form className="post-form" onSubmit={submit}>
        <textarea
          value={form.content}
          onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))}
          placeholder="Share a win, goal, or health update"
          required
        />
        <div>
          <select value={form.mood} onChange={(event) => setForm((current) => ({ ...current, mood: event.target.value }))}>
            <option>Motivated</option>
            <option>Focused</option>
            <option>Tired</option>
            <option>Celebrating</option>
          </select>
          <button className="primary-button compact" type="submit">Post</button>
        </div>
      </form>

      <section className="feed">
        {posts.map((post) => (
          <article className="post" key={post.id}>
            <div className="post-meta">
              <strong>{post.author_name}</strong>
              <span>{post.mood}</span>
            </div>
            <p>{post.content}</p>
            <button className="like-button" onClick={() => like(post.id)}>
              <HeartPulse size={16} /> {post.likes} likes
            </button>
          </article>
        ))}
        {posts.length === 0 && <p className="empty-state">No community posts yet.</p>}
      </section>
    </>
  );
}

function Coach({ fetcher }) {
  const [messages, setMessages] = useState([
    {
      role: "coach",
      text: "Ask me about your meals, protein, calories, macros, fat loss, or what to eat next.",
    },
  ]);
  const [input, setInput] = useState("");
  const quickQuestions = [
    "How is my protein today?",
    "What should I eat next?",
    "Am I over my calories?",
    "Give me fat loss suggestions",
  ];

  async function ask(question) {
    const text = question || input;
    if (!text.trim()) return;

    setMessages((current) => [...current, { role: "user", text }]);
    setInput("");

    const response = await fetcher("/chat", {
      method: "POST",
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();

    setMessages((current) => [
      ...current,
      {
        role: "coach",
        text: response.ok ? data.reply : data.detail || "I could not answer that right now.",
      },
    ]);
  }

  function submit(event) {
    event.preventDefault();
    ask();
  }

  return (
    <>
      <PageTitle title="AI Coach" subtitle="Meal-aware suggestions based on today's logs and your goals." />
      <section className="coach-panel">
        <div className="quick-questions">
          {quickQuestions.map((question) => (
            <button type="button" key={question} onClick={() => ask(question)}>
              {question}
            </button>
          ))}
        </div>

        <div className="chat-window">
          {messages.map((message, index) => (
            <article className={`chat-bubble ${message.role}`} key={`${message.role}-${index}`}>
              {message.text}
            </article>
          ))}
        </div>

        <form className="chat-input" onSubmit={submit}>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about your meals or macros"
          />
          <button className="primary-button compact" type="submit">Ask</button>
        </form>
      </section>
    </>
  );
}

function PageTitle({ title, subtitle }) {
  return (
    <header className="page-title">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </header>
  );
}

function Stat({ label, value, tone }) {
  return (
    <article className={`stat-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function GoalProgress({ label, value, goal, unit }) {
  const percent = goal > 0 ? Math.min(Math.round((value / goal) * 100), 100) : 0;

  return (
    <article className="goal-progress">
      <div>
        <span>{label}</span>
        <strong>{value} / {goal} {unit}</strong>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
    </article>
  );
}

function RecentList({ title, items, fields }) {
  return (
    <article className="recent-panel">
      <h2>{title}</h2>
      {items.length === 0 ? (
        <p className="empty-state">No data yet.</p>
      ) : (
        items.map((item) => (
          <div className="mini-row" key={item.id}>
            {fields.map((field) => (
              <span key={field}>{String(item[field])}</span>
            ))}
          </div>
        ))
      )}
    </article>
  );
}

createRoot(document.getElementById("root")).render(<App />);
