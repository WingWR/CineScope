import { ApiClient } from "./client";
import { API_BASE_URL } from "./config";

export const backendApiClient = new ApiClient(API_BASE_URL, "CineScope backend API");
