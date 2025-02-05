import asyncio
from collections import deque

import numpy as np
import pygame


class VisualInterface:
    def __init__(self, width=400, height=400):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("My Operator")
        self.clock = pygame.time.Clock()

        # Remove any image/icon usage.
        # All visuals will be drawn in white.
        self.draw_color = (255, 255, 255)  # White

        self.is_active = False
        self.is_assistant_speaking = False

        self.base_radius = 100
        self.current_radius = self.base_radius

        self.energy_queue = deque(maxlen=50)  # Store last 50 energy values
        self.update_interval = 0.05  # Update every 50ms
        self.max_energy = 1.0  # For dynamic energy normalization

        # Attributes for the sound wave animation
        self.wave_phase = 0.0  # Phase for smooth wave movement
        self.transition_factor = (
            0.0  # 0.0 => pure circle (listening), 1.0 => full sound wave (speaking)
        )

    async def update(self):
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        # Use a black background for contrast with white visuals.
        self.screen.fill((0, 0, 0))

        # Smoothly adjust the circle radius based on the energy values.
        target_radius = self.base_radius
        if self.energy_queue:
            normalized_energy = np.mean(self.energy_queue) / (self.max_energy or 1.0)
            target_radius += int(normalized_energy * self.base_radius)
        self.current_radius += (target_radius - self.current_radius) * 0.2
        self.current_radius = min(
            max(self.current_radius, self.base_radius), self.width // 2
        )

        # Update the transition factor to blend between a circle and a sound wave.
        if self.is_assistant_speaking:
            self.transition_factor = min(1.0, self.transition_factor + 0.05)
        else:
            self.transition_factor = max(0.0, self.transition_factor - 0.05)

        # Update the wave phase for continuous smooth movement.
        self.wave_phase += 0.2

        # Calculate normalized energy for modulating the wave amplitude.
        normalized_energy = (
            np.mean(self.energy_queue) / (self.max_energy or 1.0)
            if self.energy_queue
            else 0.0
        )

        center = (self.width // 2, self.height // 2)

        # Depending on the transition factor, draw either a simple circle or a modulated sound wave.
        if self.transition_factor < 0.01:
            # Draw a simple white circle (listening state).
            pygame.draw.circle(
                self.screen, self.draw_color, center, int(self.current_radius)
            )
        else:
            # If partially transitioned, you can opt to draw the base circle first.
            if self.transition_factor < 1.0:
                pygame.draw.circle(
                    self.screen, self.draw_color, center, int(self.current_radius)
                )
            # Draw the sound wave animation.
            n_points = 100  # Number of points around the circle.
            amplitude = (
                self.transition_factor * normalized_energy * (self.current_radius * 0.3)
            )
            points = []
            for i in range(n_points):
                angle = 2 * np.pi * i / n_points
                # Two full sine waves around the circle for a rich effect.
                wave_offset = amplitude * np.sin(2 * angle + self.wave_phase)
                r = self.current_radius + wave_offset
                x = center[0] + r * np.cos(angle)
                y = center[1] + r * np.sin(angle)
                points.append((x, y))
            # Draw anti-aliased lines for a smooth, high-quality look.
            pygame.draw.aalines(self.screen, self.draw_color, True, points)

        pygame.display.flip()
        self.clock.tick(60)
        await asyncio.sleep(self.update_interval)
        return True

    def set_active(self, is_active):
        self.is_active = is_active

    def set_assistant_speaking(self, is_speaking):
        self.is_assistant_speaking = is_speaking

    def update_energy(self, energy):
        # Accept energy as a numpy array or a numeric value.
        if isinstance(energy, np.ndarray):
            energy = np.mean(np.abs(energy))
        self.energy_queue.append(energy)

        # Dynamically update max_energy for normalization purposes.
        current_max = max(self.energy_queue)
        if current_max > self.max_energy:
            self.max_energy = current_max
        elif len(self.energy_queue) == self.energy_queue.maxlen:
            self.max_energy = max(self.energy_queue)

    def process_audio_data(self, audio_data: bytes):
        """Process and update audio energy for visualization."""
        audio_frame = np.frombuffer(audio_data, dtype=np.int16)
        energy = np.abs(audio_frame).mean()
        self.update_energy(energy)


async def run_visual_interface(interface):
    while True:
        if not await interface.update():
            break


# A simple simulation of toggling between speaking and listening states.
async def simulate_state(interface):
    while True:
        interface.set_assistant_speaking(True)
        await asyncio.sleep(3)  # Simulate 3 seconds of speaking.
        interface.set_assistant_speaking(False)
        await asyncio.sleep(3)  # Simulate 3 seconds of listening.


if __name__ == "__main__":
    interface = VisualInterface()

    # For demonstration purposes, simulate audio energy updates.
    # In a real scenario, you would feed actual audio data.
    async def simulate_energy():
        import random

        while True:
            # Simulate random energy values between 0 and 5000.
            energy = random.randint(0, 5000)
            interface.update_energy(energy)
            await asyncio.sleep(0.05)

    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(
        run_visual_interface(interface), simulate_state(interface), simulate_energy()
    )
    loop.run_until_complete(tasks)
