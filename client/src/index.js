import React from 'react'
import ReactDOM from 'react-dom'
import App from './App'
import {QWebChannel} from "qwebchannel";


new QWebChannel(window.qt.webChannelTransport, function (channel) {

    window.Browser = channel.objects.backend
    window.Controller = channel.objects.controller

    ReactDOM.render (
        <React.StrictMode>
            <App/>
        </React.StrictMode>,
        document.getElementById('root')
    )

})
