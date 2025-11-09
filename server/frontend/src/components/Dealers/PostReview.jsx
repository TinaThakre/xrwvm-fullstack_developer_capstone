import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';


const PostReview = () => {
    const [dealer, setDealer] = useState({});
    const [review, setReview] = useState("");
    const [model, setModel] = useState(""); // Default to empty string
    const [year, setYear] = useState("");
    const [date, setDate] = useState("");
    const [carMakes, setCarMakes] = useState([]); // Renamed from carmodels for clarity

    let params = useParams();
    let id = params.id;
    let root_url = window.location.origin;

    // Use the correct proxy path to Django for API calls
    let dealer_url = root_url + `/djangoapp/dealer/${id}`;
    let review_url = root_url + `/djangoapp/add_review`;
    let car_makes_url = root_url + `/djangoapp/get_cars`; // Renamed URL var for clarity

    const postreview = async () => {
        let name = sessionStorage.getItem("firstname") + " " + sessionStorage.getItem("lastname");
        if (name.includes("null")) {
            name = sessionStorage.getItem("username");
        }

        if (!model || review === "" || date === "" || year === "") {
            alert("All details are mandatory");
            return;
        }

        let model_split = model.split(" ");
        let make_chosen = model_split[0];
        let model_chosen = model_split.slice(1).join(" "); // Joins model names with spaces

        let jsoninput = JSON.stringify({
            "name": name,
            "dealership": id,
            "review": review,
            "purchase": true, // Assuming purchase is true for simplicity
            "purchase_date": date,
            "car_make": make_chosen,
            "car_model": model_chosen,
            "car_year": year,
        });

        console.log("Submitting Review:", jsoninput);
        const res = await fetch(review_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: jsoninput,
        });

        const json = await res.json();
        if (json.status === 200) {
            window.location.href = window.location.origin + "/dealer/" + id;
        } else {
            alert("Review submission failed: " + json.message);
        }
    }

    const get_dealer = async () => {
        const res = await fetch(dealer_url, {
            method: "GET"
        });
        const retobj = await res.json();

        if (retobj.status === 200) {
            let dealerobjs = Array.from(retobj.dealer)
            if (dealerobjs.length > 0)
                setDealer(dealerobjs[0])
        }
    }

    // FIX: Corrected the car data fetch function
    const get_cars = async () => {
        const res = await fetch(car_makes_url, {
            method: "GET"
        });
        const retobj = await res.json();

        // Check for status 200 AND the correct 'cars' key
        if (retobj.status === 200 && retobj.cars) { 
            // Extract the array from the 'cars' key
            let carmakesarr = Array.from(retobj.cars); 
            setCarMakes(carmakesarr);
        } else {
            console.error("Failed to fetch car makes:", retobj.message || retobj);
        }
    }

    useEffect(() => {
        get_dealer();
        get_cars();
    }, []);

    return (
        <div>
            <Header />
            <div style={{ margin: "5%" }}>
                <h1 style={{ color: "darkblue" }}>{dealer.full_name}</h1>
                <textarea id='review' cols='50' rows='7' onChange={(e) => setReview(e.target.value)}></textarea>
                <div className='input_field'>
                    Purchase Date <input type="date" onChange={(e) => setDate(e.target.value)} />
                </div>
                <div className='input_field'>
                    Car Make
                    {/* FIX: Use value and onChange on select; remove 'selected' from option */}
                    <select name="cars" id="cars" value={model} onChange={(e) => setModel(e.target.value)}>
                        <option value="" disabled hidden>Choose Car Make and Model</option>
                        {carMakes.map(carMake => ( // Map over carMakes (the list of makes)
                            <optgroup label={carMake.name} key={carMake.id}>
                                {carMake.models.map(carModel => ( // Map over models within the make
                                    // Value format: "Make Model" (e.g., "Toyota Corolla")
                                    <option 
                                        value={`${carMake.name} ${carModel.name}`} 
                                        key={carModel.id}
                                    >
                                        {carMake.name} {carModel.name}
                                    </option>
                                ))}
                            </optgroup>
                        ))}
                    </select>
                </div >

                <div className='input_field'>
                    {/* Max and Min values should be set on the input tag */}
                    Car Year <input type="number" onChange={(e) => setYear(e.target.value)} max={2023} min={2015} />
                </div>

                <div>
                    <button className='postreview' onClick={postreview}>Post Review</button>
                </div>
            </div>
        </div>
    )
}
export default PostReview