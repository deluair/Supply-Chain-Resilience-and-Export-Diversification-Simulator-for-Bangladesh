# src/simulation_core/event_manager.py
import simpy
import logging
from typing import Callable, Any, List, Tuple
from enum import Enum, auto

logger = logging.getLogger(__name__)

class EventType(Enum):
    GENERAL = auto()
    DISRUPTION_START = auto()
    DISRUPTION_END = auto()
    POLICY_CHANGE = auto()
    AGENT_ACTION = auto()
    # Add more specific event types as needed

class Event:
    """
    Represents a scheduled event in the simulation.
    """
    def __init__(self, step: int, event_type: EventType, action: Callable, description: str = "", args: tuple = (), kwargs: dict = None):
        self.step = step  # Simulation step (e.g., day) at which the event occurs
        self.event_type = event_type
        self.action = action  # The function/method to call when the event triggers
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}
        self.description = description if description else f"Event type {event_type.name}"
        self.triggered = False

    def trigger(self):
        """Executes the event's action."""
        if not self.triggered:
            logger.info(f"Triggering event: {self.description} at step {self.step}")
            try:
                self.action(*self.args, **self.kwargs)
                self.triggered = True
            except Exception as e:
                logger.error(f"Error executing event action for '{self.description}': {e}", exc_info=True)
        else:
            logger.warning(f"Event '{self.description}' attempted to trigger multiple times.")

    def __lt__(self, other):
        # For sorting events by step, then by some other criteria if needed (e.g., priority)
        if not isinstance(other, Event):
            return NotImplemented
        return self.step < other.step

    def __repr__(self):
        return f"<Event(step={self.step}, type={self.event_type.name}, desc='{self.description}', triggered={self.triggered})>"


class EventManager:
    """
    Manages and processes scheduled events within the SimPy environment.
    """
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.event_queue: List[Event] = [] # Using a list, can be optimized with heapq if performance critical
        logger.info("EventManager initialized.")

    def schedule_event(self, step: int, event_type: EventType, action: Callable, description: str = "", args: tuple = (), kwargs: dict = None):
        """
        Schedules a new event.
        The 'step' is the absolute simulation step (e.g., day number).
        """
        if step < self.env.now: # self.env.now is the current simulation time
            logger.warning(f"Attempted to schedule event '{description}' for past step {step} (current: {self.env.now}). Skipping.")
            return

        event = Event(step, event_type, action, description, args, kwargs)
        # Insert in sorted order (or sort later, or use heapq)
        self.event_queue.append(event)
        self.event_queue.sort() # Keep sorted by step; for large numbers of events, heapq is better
        logger.debug(f"Scheduled event: {event}")

    def process_events(self, current_step: int):
        """
        Processes all events scheduled for the current simulation step.
        """
        triggered_count = 0
        # Iterate carefully as triggering an event might schedule new events
        # Process events for current_step. Since queue is sorted, they will be at the beginning.
        
        events_to_trigger_now = []
        remaining_events = []

        for event in self.event_queue:
            if event.step == current_step and not event.triggered:
                events_to_trigger_now.append(event)
            else:
                remaining_events.append(event)
        
        self.event_queue = remaining_events # Update queue with non-triggered or future events

        if events_to_trigger_now:
            logger.info(f"Processing {len(events_to_trigger_now)} events for step {current_step}.")
            for event in events_to_trigger_now:
                event.trigger()
                triggered_count += 1
        
        return triggered_count

    # SimPy process method for continuous event checking (alternative to manual process_events call)
    # def run(self):
    #     """A SimPy process that continuously checks and triggers events."""
    #     while True:
    #         # Find events for self.env.now
    #         events_for_now = [e for e in self.event_queue if e.step == self.env.now and not e.triggered]
            
    #         for event in events_for_now:
    #             event.trigger()
    #             # self.event_queue.remove(event) # Be careful with modification while iterating
            
    #         # Clean up triggered events (if not removed above)
    #         self.event_queue = [e for e in self.event_queue if not e.triggered or e.step > self.env.now]
            
    #         # Determine next event time
    #         if not self.event_queue:
    #             yield self.env.timeout(1) # Wait a step if no events, or could be infinity
    #         else:
    #             next_event_time = min(e.step for e in self.event_queue if e.step >= self.env.now)
    #             yield self.env.timeout(next_event_time - self.env.now)


if __name__ == '__main__':
    # Example Usage
    logging.basicConfig(level=logging.DEBUG)

    sim_env = simpy.Environment()
    event_manager = EventManager(sim_env)

    def example_action(message: str, step: int):
        logger.info(f"Example action triggered at step {step} with message: '{message}' (SimTime: {sim_env.now})")

    event_manager.schedule_event(step=5, event_type=EventType.GENERAL, action=example_action, description="Test Event 1", args=("Hello from Event 1", 5))
    event_manager.schedule_event(step=2, event_type=EventType.DISRUPTION_START, action=example_action, description="Test Event 2", args=("Disruption Starting!", 2))
    event_manager.schedule_event(step=5, event_type=EventType.POLICY_CHANGE, action=example_action, description="Test Event 3", args=("Policy Update!", 5))

    def simulation_process(env, manager):
        for i in range(10): # Simulate 10 steps
            logger.debug(f"--- Current Simulation Step: {i} (SimTime: {env.now}) ---")
            manager.process_events(i) # Manually process events for current step 'i'
            yield env.timeout(1) # Advance simulation time by 1 unit

    sim_env.process(simulation_process(sim_env, event_manager))
    sim_env.run()

    logger.info("EventManager example finished.")
