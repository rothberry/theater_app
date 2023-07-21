// 📚 Review With Students:
import { Route, Routes, useNavigate } from "react-router-dom"
import { createGlobalStyle } from "styled-components"
import { useEffect, useState } from "react"
import Home from "./components/Home"
import ProductionForm from "./components/ProductionForm"
import ProductionEdit from "./components/ProductionEdit"
import Navigation from "./components/Navigation"
import ProductionDetail from "./components/ProductionDetail"
import NotFound from "./components/NotFound"
import Authentication from "./components/Authentication"

function App() {
	const [productions, setProductions] = useState([])
	const [productionEdit, setProductionEdit] = useState([])
	const [currentUser, setUser] = useState(null)
	const history = useNavigate()

	useEffect(() => {
		fetchUser()
		fetchProductions()
	}, [])

	const fetchProductions = () =>
		fetch("/productions")
			.then((res) => res.json())
			.then(setProductions)

	const fetchUser = () => {
		fetch("/authorized")
			.then((res) => res.json())
			.then((userResponse) => {
				if (!userResponse.errors) {
					setUser(userResponse)
				}
			})
	}

	const addProduction = (production) =>
		setProductions((current) => [...current, production])

	const updateProduction = (updated_production) =>
		setProductions((productions) =>
			productions.map((production) =>
				production.id === updated_production.id ? updated_production : production
			)
		)

	const deleteProduction = (deleted_production) =>
		setProductions((productions) =>
			productions.filter(
				(production) => production.id !== deleted_production.id
			)
		)

	const handleEdit = (production) => {
		setProductionEdit(production)
		history.push(`/productions/edit/${production.id}`)
	}

	if (!!currentUser) {
		return (
			<>
				<GlobalStyle />
				<Navigation setUser={setUser} handleEdit={handleEdit} loggedIn={!!currentUser}/>
				<h1>{currentUser ? currentUser.name : "Not Logged In"}</h1>
				<Routes>
					<Route
						path="/productions/new"
						element={<ProductionForm addProduction={addProduction} />}
					/>
					<Route
						path="/productions/edit/:id"
						element={
							<ProductionEdit
								updateProduction={updateProduction}
								productionEdit={productionEdit}
							/>
						}
					/>
					<Route
						path="/productions/:id"
						element={
							<ProductionDetail
								handleEdit={handleEdit}
								deleteProduction={deleteProduction}
							/>
						}
					/>
					<Route exact path="/" element={<Home productions={productions} />} />
					<Route element={<NotFound />} />
				</Routes>
			</>
		)
	} else {
		return (
			<>
				<GlobalStyle />
				<Navigation setUser={setUser} handleEdit={handleEdit} loggedIn={!!currentUser}/>
				<Routes>
					<Route
						exact
						path="/authentication"
						element={<Authentication setUser={setUser} />}
					/>
				</Routes>
			</>
		)
	}
}

export default App

const GlobalStyle = createGlobalStyle`
    body{
      background-color: black; 
      color:white;
    }
    `
