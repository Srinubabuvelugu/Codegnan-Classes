
import React, { useState } from "react";
import axios from "axios";

function App() {

    const [name, setName] = useState("");
    const [course, setCourse] = useState("");
    const [message, setMessage] = useState("");
    const [data, setData] = useState([]);

    async function registerStudent(e) {

        e.preventDefault();

        try {
            let response = await axios.post(
                "http://127.0.0.1:5000/api/students",
                {
                    name: name,
                    course: course
                }
            );

            setMessage(response.data.message);

            setName("");
            setCourse("");

        }
        catch (error) {
            console.log(error);
            setMessage("Registration failed");
        }
    }

    async function getstudents() {

        try {
            let response = await axios.get(
                "http://127.0.0.1:5000/api/students"
            );

            setData(response.data);
            setMessage("Students retrieved successfully");

        }
        catch (error) {
            console.log(error);
            setMessage("Failed to get students data");
        }
    }

    return (
        <div>

            <h1>Student Registration</h1>

            <form onSubmit={registerStudent}>

                <label>Student Name</label>

                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />

                <br /><br />

                <label>Course</label>

                <input
                    type="text"
                    value={course}
                    onChange={(e) => setCourse(e.target.value)}
                    required
                />

                <br /><br />

                <button type="submit">
                    Register Student
                </button>

            </form>

            <h3>{message}</h3>

            <button onClick={getstudents}>
                Students
            </button>

            <h2>Students List</h2>

            <table border="1" cellPadding="10">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Course</th>
                    </tr>
                </thead>

                <tbody>

                    {data.map((student) => (

                        <tr key={student.id}>
                            <td>{student.id}</td>
                            <td>{student.name}</td>
                            <td>{student.course}</td>
                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}

export default App;
