import axios from 'axios';

// create axios instance with fastapi base url to use
const api = axios.create({
    baseURL: "http://localhost:8000/api"       // change to fastapi url later
});

export default api;