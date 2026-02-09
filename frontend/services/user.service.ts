import api from "@/lib/api";

export interface UserPreferences {
  selected_tags: string[];
  available_tags: string[];
}

export const userService = {
  // קבלת ההעדפות - עכשיו דרך ה-Profile
  async getPreferences() {
    const response = await api.get<UserPreferences>("/profile/preferences");
    return response.data;
  },

  // עדכון העדפות - שים לב שזה POST כדי להתאים לקוד הפייתון שלך
  async updatePreferences(tags: string[]) {
    const response = await api.post("/profile/preferences", { tags });
    return response.data;
  }
};