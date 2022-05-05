import { BrowserRouter, Routes, Route } from 'react-router-dom';
import React from 'react';
import Home from '../pages/Home';
import './Body.css';
import Login from '../pages/Login';
import Register from '../pages/Register';
import PostDetail from '../pages/PostDetail';



export default function Body() {
    return (
            <BrowserRouter>
                <Routes>
                    <Route path ='/' element ={<Home />} /> 
                    
                    <Route  path ='/login' element ={<Login />} />
                    <Route  path ='/register' element ={<Register />} />
                    <Route  path ='/postdetail/:postId/' element ={<PostDetail />} />
                </Routes> 
            </BrowserRouter>
       
    )
}