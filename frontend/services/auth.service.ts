import api from "@/lib/api";

// נגדיר טיפוסים כדי שהכל יהיה מסודר
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  email: string;      // הגיע מהלוג שלך
  user_id: string;    // הגיע מהלוג שלך
  role?: 'user' | 'admin'; // אם ה-Backend לא מחזיר role כרגע, נטפל בזה
}

export const authService = {
  async login(credentials: LoginCredentials) {
    const response = await api.post<AuthResponse>("/auth/login", credentials);
    return response.data;
  },

  // פונקציית הרשמה
  async signup(credentials: SignupCredentials) {
    const response = await api.post("/auth/signup", credentials);
    return response.data;
  },
  
  // פונקציית יציאה (אופציונלי, כרגע זה רק בצד לקוח אבל הכנה לעתיד)
  async logout() {
    // אם בעתיד נצטרך להודיע לשרת על יציאה
  }
};