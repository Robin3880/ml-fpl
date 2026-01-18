import axios from 'axios';

// create axios instance with fastapi base url to use
const api = axios.create({
    baseURL: "https://fpl-fastapi.azurewebsites.net/api"
});

export default api;