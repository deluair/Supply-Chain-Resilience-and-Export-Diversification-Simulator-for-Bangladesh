# src/agents/disruption_agent.py
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DisruptionAgent(BaseAgent):
    """
    Represents agents that introduce or manage disruptions in the supply chain.
    """
    def __init__(self, agent_id=None, simulation_engine=None, config=None):
        super().__init__(agent_id, simulation_engine, config)
        self.disruption_type = self.config.get("disruption_type", "GenericDisruption")
        self.magnitude = self.config.get("magnitude", 0.1) # Example: 10% impact
        self.duration = self.config.get("duration", 1) # Example: 1 day duration
        self.target_scope = self.config.get("target_scope", "all") # e.g., "Port:Chittagong", "Sector:RMG"
        self.start_step = self.config.get("start_step", -1) # Step at which disruption begins, -1 if immediate or event-triggered
        self.active = False
        logger.info(f"DisruptionAgent {self.agent_id} ({self.disruption_type}) initialized. Target: {self.target_scope}, Mag: {self.magnitude}, Dur: {self.duration}, Start: {self.start_step}")

    def step(self, current_step):
        """
        Simulates the agent's behavior for one time step.
        - Check if disruption should start, be active, or end.
        - Apply impact to targeted entities if active.
        """
        if not self.active and self.start_step >= 0 and current_step >= self.start_step:
            self.active = True
            self.duration_remaining = self.duration
            logger.info(f"Disruption {self.agent_id} ({self.disruption_type}) now ACTIVE at step {current_step}. Target: {self.target_scope}")
            self.apply_impact(current_step)

        elif self.active:
            if self.duration_remaining > 0:
                logger.debug(f"Disruption {self.agent_id} ongoing. {self.duration_remaining} steps remaining.")
                # Potentially re-apply or continue impact logic here if needed daily
                self.duration_remaining -= 1
            else:
                self.active = False
                logger.info(f"Disruption {self.agent_id} ({self.disruption_type}) has ENDED at step {current_step}.")
                self.remove_impact(current_step)

    def apply_impact(self, current_step):
        """
        Placeholder for logic to apply the disruption's impact.
        This would typically involve interacting with the simulation_engine 
        or directly with affected agents/nodes if references are available.
        """
        logger.warning(f"Disruption {self.agent_id} apply_impact: Targeting '{self.target_scope}' - actual impact logic not yet implemented.")
        # Example: Find target nodes/agents via simulation_engine.supply_chain_network
        # and modify their properties or trigger events.

    def remove_impact(self, current_step):
        """
        Placeholder for logic to remove or revert the disruption's impact.
        """
        logger.warning(f"Disruption {self.agent_id} remove_impact: Targeting '{self.target_scope}' - actual removal logic not yet implemented.")

    def __repr__(self):
        return f"<DisruptionAgent(id={self.agent_id}, type={self.disruption_type}, active={self.active})>"
