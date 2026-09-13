AGENTS_BY_ROLE = {
    "Duelist": ["Jett", "Reyna", "Raze", "Phoenix", "Yoru", "Neon", "Iso"],
    "Initiator": ["Sova", "Breach", "Skye", "KAY/O", "Fade", "Gekko", "Tejo"],
    "Controller": ["Omen", "Viper", "Brimstone", "Astra", "Harbor", "Clove"],
    "Sentinel": ["Killjoy", "Cypher", "Sage", "Chamber", "Deadlock", "Vyse"]
}

def get_role_from_agent(agent_name: str) -> str:
    for role, agents in AGENTS_BY_ROLE.items():
        if any(a.lower() == agent_name.lower() for a in agents):
            return role
    return "Duelist"
