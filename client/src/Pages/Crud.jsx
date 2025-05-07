import { useState, useEffect } from "react"

export default function Crud (){
    const [list, setList]= useState([]);
    const [data, setData] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        email:''
    });
    const handleOnchange = (e) => {
    const {name, value} = e.target;
    setFormData(preVal=> ({
        ...preVal,
        [name]: value
    }))
    }
    const onSubmitChange = (e) => {
        e.preventDefault();
        setList((prevList) => [
            ...prevList,
            {...formData}
        ]);
        
        console.log("Updated List:", list);  // This won't show the updated state immediately
    };
    useEffect(()=> {
        setData(list)
    }, [list])
    return(
    <>
        <form onSubmit={(e)=> onSubmitChange(e)} >
            <h3>AddFoerm</h3>
            <input class="name" type="text" name="name" id="" value={formData.name} onChange={(e)=> handleOnchange(e)} />
            <input type="text" name="email" id="" value={formData.email} onChange={(e)=> handleOnchange(e)}/>
            <button>Sumit</button>
        </form>
        <table>
            <thead>
                <tr>
                    <th>Nmae</th>
                    <th>Email</th>
                    </tr>
            </thead>
            <tbody>
                    {
                        (data ? (
                            data.map((item, index) => (
                                <tr key={index}>
                                    <td>{list.name}</td>
                                    <td>{list.email}</td>
                                </tr>
                            ) )
                        ):'Nodata')
                    }
            </tbody>
        </table>
    </>
    )
}