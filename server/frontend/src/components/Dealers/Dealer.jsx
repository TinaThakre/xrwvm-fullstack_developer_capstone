import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import positive_icon from "../assets/positive.png"
import neutral_icon from "../assets/neutral.png"
import negative_icon from "../assets/negative.png"
import review_icon from "../assets/reviewbutton.png"
import Header from '../Header/Header';

const Dealer = () => {
    // State initialization
    const [dealer, setDealer] = useState({});
    const [reviews, setReviews] = useState([]);
    const [unreviewed, setUnreviewed] = useState(false);
    const [postReview, setPostReview] = useState(<></>);

    // URL Construction
    let params = useParams();
    let id = params.id;
    let root_url = window.location.origin; 
    
    let dealer_url = root_url + `/djangoapp/dealer/${id}`;
    let reviews_url = root_url + `/djangoapp/reviews/dealer/${id}`;
    let post_review_link = root_url + `/postreview/${id}`;
    
    // --- API Fetch Functions ---

    const get_dealer = async () => {
        const res = await fetch(dealer_url, {
            method: "GET"
        });
        const retobj = await res.json();

        // Check for correct status code AND if the expected 'dealer' key exists
        if (retobj.status === 200 && retobj.dealer) {
            // The API returns the dealer object under a 'dealer' key
            setDealer(retobj.dealer); // Directly set the dealer object
        }
    }

    const get_reviews = async () => {
        const res = await fetch(reviews_url, {
            method: "GET"
        });
        const retobj = await res.json();

        // Check for correct status code AND if the expected 'reviews' key exists
        if (retobj.status === 200 && retobj.reviews) {
            if (retobj.reviews.length > 0) {
                setReviews(retobj.reviews)
            } else {
                setUnreviewed(true);
            }
        }
    }

    // --- Utility Functions ---

    const senti_icon = (sentiment) => {
        let icon = sentiment === "positive" ? positive_icon : sentiment === "negative" ? negative_icon : neutral_icon;
        return icon;
    }

    // --- Effect Hook ---
    useEffect(() => {
        get_dealer();
        get_reviews();
        
        // Only show "Post Review" button if the user is logged in
        if (sessionStorage.getItem("username")) {
            setPostReview(
                <a href={post_review_link}>
                    <img 
                        src={review_icon} 
                        style={{width:'10%',marginLeft:'10px',marginTop:'10px'}} 
                        alt='Post Review'
                    />
                </a>
            )
        }
    }, [id]); 

    // --- Component Render ---
    return(
        <div style={{margin:"20px"}}>
            <Header/>
            
            {/* DEFENSIVE RENDERING: Only render details if the dealer object has data (full_name) */}
            {dealer.full_name ? (
                <>
                <div style={{marginTop:"10px"}}>
                    {/* Dealer Name and Post Review Button */}
                    <h1 style={{color:"grey"}}>{dealer.full_name}{postReview}</h1> 
                    {/* Dealer Location Details */}
                    <h4 style={{color:"grey"}}>{dealer['city']}, {dealer['address']}, Zip - {dealer['zip']}, {dealer['state']} </h4>
                </div>

                <div className="reviews_panel">
                    {/* Display Reviews */}
                    {reviews.length === 0 && unreviewed === false ? (
                        <span>Loading Reviews....</span>
                    ): unreviewed === true ? (
                        <div>No reviews yet! </div>
                    ) : (
                        reviews.map(review => (
                            <div className='review_panel' key={review.id}> 
                                <img src={senti_icon(review.sentiment)} className="emotion_icon" alt='Sentiment'/>
                                <div className='review'>{review.review}</div>
                                <div className="reviewer">
                                    {review.name} 
                                    {review.purchase ? 
                                        ` - ${review.car_make} ${review.car_model} ${review.car_year}` 
                                        : ''
                                    }
                                </div>
                            </div>
                        ))
                    )}
                </div> 
                </>
            ) : (
                // Show a loading message or nothing while data is fetching
                <div style={{padding: '20px'}}>Loading dealer details...</div>
            )}
        </div>
    )
}

export default Dealer;