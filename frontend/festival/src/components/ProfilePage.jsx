import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import axios from "axios";
import addpro from './addpro.webp'; 
import pro1 from './pro1.jpg';   
const ProfilePage = () => {
    const navigate = useNavigate();
    const { candidateId } = useParams();
    const { state } = useLocation(); 
    const [name, setName] = useState(null);
    const [votes, setVotes] = useState(0);
    const [profileImage, setProfileImage] = useState(null);
    const [category, setCategory] = useState(state?.category || ""); 

    useEffect(() => {
        const fetchData = async () => {
            try {
                const nameProfileResponse = await axios.get(
                    `http://127.0.0.1:5000/get_name_profile_image/${candidateId}`,
                    { withCredentials: true }
                );
                setName(nameProfileResponse.data.full_name);
                setProfileImage(nameProfileResponse.data.profileImage);
            } catch (error) {
                console.error("Error fetching profile data:", error);
               
            }
        };
        
        const fetchVotes = async () => {
            try {
                const votesResponse = await axios.get(`http://127.0.0.1:5000/candidate/${candidateId}/votes`, {
                    withCredentials: true
                });
                setVotes(votesResponse.data.vote_count);
            } catch (error) {
                console.error("Error fetching vote count:", error);
               
            }
        };

        if (candidateId !== "0") { 
            fetchData();
            fetchVotes(); 
            const intervalId = setInterval(fetchVotes, 5000); 

            return () => clearInterval(intervalId); 

        }
    }, [candidateId]);

    const handleImageChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("profile_image", file);

        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/upload_profile_image",
                formData,
                { withCredentials: true }
            );
            setProfileImage(response.data.profileImage);
        } catch (error) {
            console.error("Error uploading image:", error);
        }
    };

    return (
        <div style={styles.container}>
            {name ? (
                <h2 style={styles.name}>Name: {name}</h2>
            ) : (
                <h2 style={styles.name}>Name: Not Available</h2>
            )}
            {category && <h3 style={styles.category}>Category: {category}</h3>}
            <div style={styles.profileIcon} onClick={() => document.getElementById("fileInput").click()}>
                <img
                    src={profileImage || addpro}
                    alt="Profile"
                    style={styles.profileImage}
                />
            </div>
            <input
                type="file"
                id="fileInput"
                accept="image/*"
                onChange={handleImageChange}
                style={{ display: "none" }}
            />
            <p style={styles.votes}>Votes: {votes}</p>
            <div style={styles.profileIcon} onClick={() => navigate(`/verification-form/${candidateId}`)}>
                <img src={pro1} alt="Account" style={styles.accountImage} />
            </div>
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: "#5c0e0e",
        color: "white",
        textAlign: "center",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
    },
    name: {
        fontSize: "1.5rem",
        marginBottom: "10px",
        position: "absolute",
        top: "20px",
    },
    category: {
        fontSize: "1.2rem",
        marginBottom: "20px",
        position: "absolute",
        top: "60px",
    },
    votes: {
        fontSize: "1.2rem",
        position: "absolute",
        bottom: "20px",
        left: "20px",
    },
    profileIcon: {
        width: "150px",
        height: "150px",
        backgroundColor: "transparent",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
    },
    profileImage: {
        width: "100%",
        height: "100%",
        borderRadius: "50%",
    },
    accountImage: {
        width: "80px",
        height: "80px",
        borderRadius: "50%",
        position: "absolute",
        bottom: "20px",
        right: "20px",
        cursor: "pointer",
    },
};

export default ProfilePage;
