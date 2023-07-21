import { useState } from "react"
import { Link } from "react-router-dom"
import styled from "styled-components"
import { useNavigate } from "react-router-dom"
import { GiHamburgerMenu } from "react-icons/gi"

function Navigation({ setUser, loggedIn }) {
	const [menu, setMenu] = useState(false)
	const history = useNavigate()

	const handleLogout = () => {
		fetch("/logout", { method: "DELETE" }).then(() => {
			setUser(null)
			// setUser({})
			history("/authentication")
		})
	}

	return (
		<Nav>
			<NavH1>Flatiron Theater Company</NavH1>
			<Menu>
				{!menu ? (
					<div onClick={() => setMenu(!menu)}>
						<GiHamburgerMenu size={30} />
					</div>
				) : (
					<ul>
						<li onClick={() => setMenu(!menu)}>x</li>
						<li>
							<Link to="/productions/new">New Production</Link>
						</li>
						<li>
							<Link to="/"> Home</Link>
						</li>
						{loggedIn ? (
							<li onClick={handleLogout}> Logout </li>
						) : (
							<li>
								<Link to="/authentication"> Login/Signup</Link>
							</li>
						)}
					</ul>
				)}
			</Menu>
		</Nav>
	)
}

export default Navigation

const NavH1 = styled.h1`
	font-family: "Splash", cursive;
`
const Nav = styled.div`
	display: flex;
	justify-content: space-between;
`

const Menu = styled.div`
	display: flex;
	align-items: center;
	a {
		text-decoration: none;
		color: white;
		font-family: Arial;
	}
	a:hover {
		color: pink;
	}
	ul {
		list-style: none;
	}
`
