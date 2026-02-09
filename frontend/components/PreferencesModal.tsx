"use client";

import { useState, useEffect } from "react";
import { X, Check } from "lucide-react";
import { userService } from "@/services/user.service";

interface PreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void; // כדי לרענן את הפיד אחרי שמירה
}

export default function PreferencesModal({ isOpen, onClose, onSave }: PreferencesModalProps) {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // טעינת הנתונים בפתיחת החלון
  useEffect(() => {
    if (isOpen) {
      loadPreferences();
    }
  }, [isOpen]);

  const loadPreferences = async () => {
    try {
      const data = await userService.getPreferences();
      setSelectedTags(data.selected_tags);
      setAvailableTags(data.available_tags);
    } catch (err) {
      console.error("Failed to load prefs", err);
    }
  };

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter((t) => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await userService.updatePreferences(selectedTags);
      onSave(); // עדכון הפיד הראשי
      onClose();
    } catch (err) {
      alert("Failed to save preferences");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-2xl border border-gray-800 bg-[#0A0A0A] p-6 shadow-2xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">Customize Your Feed</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white" title="Close preferences">
            <X className="h-6 w-6" />
          </button>
        </div>

        <p className="mb-4 text-sm text-gray-400">
          Select topics you are interested in. We will use AI to curate the best news for you.
        </p>

        <div className="flex flex-wrap gap-3 mb-8">
          {availableTags.map((tag) => {
            const isSelected = selectedTags.includes(tag);
            return (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${
                  isSelected
                    ? "bg-primary text-white shadow-lg shadow-primary/25 ring-2 ring-primary/50"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                {tag}
                {isSelected && <Check className="h-3 w-3" />}
              </button>
            );
          })}
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-400 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="rounded-lg bg-primary px-6 py-2 text-sm font-bold text-white hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Preferences"}
          </button>
        </div>
      </div>
    </div>
  );
}