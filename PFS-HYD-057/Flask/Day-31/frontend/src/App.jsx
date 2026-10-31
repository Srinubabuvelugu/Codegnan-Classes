import React, { useState } from "react";
import Demo from "./demo";
import axios from "axios";

// import React, { useState } from "react";
// import axios from "axios";

function App() {

    const [name, setName] = useState("");
    const [course, setCourse] = useState("");
    const [message, setMessage] = useState("");

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

            console.log(response.data);

            setName("");
            setCourse("");

        }
        catch (error) {
            console.log(error);
            setMessage("Registration failed");
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

        </div>
    );
}

export default App;
