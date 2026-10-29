import React, { useState } from "react";
import Demo from "./demo";
import axios from "axios";
function App() {
    let count = 0;
    const [res,setResult] = useState('')
    const [student,setStudent] = useState([])
    async function fun(){
        let response = await axios.get('http://127.0.0.1:5000/api/students')
        setStudent(response.data)
        console.log(student)
    }
    function inc(){
        let refele1 = document.getElementById('ref1')
        count += 1
        refele1.innerText = count
    }
    return (
        <div>
            <h1>Student Details</h1>

            <button onClick={fun}>Details</button>

            {student.map((s) => (
                <div key={s.id}>
                    <p>ID: {s.id}</p>
                    <p>Name: {s.name}</p>
                    <p>Course: {s.course}</p>
                    <hr />
                </div>
            ))}
            <h1 id="ref1">{count}</h1>
            <button onClick={inc}>inc</button>
        </div>
        
    );
}

export default App;
