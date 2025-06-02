# src/agents/base_agent.py
import uuid

class BaseAgent:
    """
    Base class for all agents in the simulation.
    """
    def __init__(self, agent_id=None, simulation_engine=None, config=None):
        self.agent_id = agent_id if agent_id else str(uuid.uuid4())
        self.simulation_engine = simulation_engine
        self.config = config if config else {}
        # self.env = simulation_engine.env # If using SimPy

    def step(self, current_step):
        """
        Represents a single step or action taken by the agent in a simulation cycle.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the 'step' method.")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id})>"
