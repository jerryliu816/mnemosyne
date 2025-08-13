#!/usr/bin/env python3
"""
Generate system architecture diagram for Mnemosyne project
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Define colors
pi_color = '#E74C3C'      # Red for Raspberry Pi
server_color = '#3498DB'   # Blue for server
ai_color = '#9B59B6'      # Purple for AI services
db_color = '#2ECC71'      # Green for database
web_color = '#F39C12'     # Orange for web interface
gpio_color = '#34495E'    # Dark gray for GPIO

# Title
ax.text(7, 9.5, 'Mnemosyne Visual Memory System', 
        fontsize=20, fontweight='bold', ha='center')

# Raspberry Pi Device Section (Left side)
pi_box = FancyBboxPatch((0.5, 6), 3.5, 3, 
                        boxstyle="round,pad=0.1", 
                        facecolor=pi_color, alpha=0.3, 
                        edgecolor=pi_color, linewidth=2)
ax.add_patch(pi_box)
ax.text(2.25, 8.5, 'Raspberry Pi Camera Device', 
        fontsize=12, fontweight='bold', ha='center')
ax.text(2.25, 8.1, '(cam4.py)', fontsize=10, ha='center', style='italic')

# Pi Camera
cam_box = FancyBboxPatch((0.8, 7.2), 1.2, 0.6, 
                         boxstyle="round,pad=0.05", 
                         facecolor='white', edgecolor=pi_color)
ax.add_patch(cam_box)
ax.text(1.4, 7.5, 'PiCamera2', fontsize=9, ha='center', fontweight='bold')

# GPIO Controls
gpio_box = FancyBboxPatch((2.2, 7.2), 1.5, 0.6, 
                          boxstyle="round,pad=0.05", 
                          facecolor=gpio_color, alpha=0.3, edgecolor=gpio_color)
ax.add_patch(gpio_box)
ax.text(2.95, 7.5, 'GPIO Controls', fontsize=9, ha='center', fontweight='bold')
ax.text(2.95, 7.3, 'Buttons & LEDs', fontsize=8, ha='center')

# Network transmission
ax.text(2.25, 6.7, 'Network Client', fontsize=10, ha='center')
ax.text(2.25, 6.4, '• Image Capture\n• Base64 Encoding\n• HTTP POST', 
        fontsize=8, ha='center', va='top')

# Flask Server Section (Center-right)
server_box = FancyBboxPatch((5, 6), 3.5, 3, 
                           boxstyle="round,pad=0.1", 
                           facecolor=server_color, alpha=0.3, 
                           edgecolor=server_color, linewidth=2)
ax.add_patch(server_box)
ax.text(6.75, 8.5, 'Flask Content Server', 
        fontsize=12, fontweight='bold', ha='center')
ax.text(6.75, 8.1, '(app2.py)', fontsize=10, ha='center', style='italic')

# Server components
ax.text(6.75, 7.6, 'REST API Endpoints:', fontsize=10, ha='center', fontweight='bold')
ax.text(6.75, 7.2, '• /add_content (POST)\n• /get_contents (GET)\n• /contents (Web UI)\n• /query (NL Search)', 
        fontsize=9, ha='center', va='top')

# Arrow from Pi to Server
arrow1 = ConnectionPatch((4, 7.5), (5, 7.5), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, 
                        mutation_scale=20, fc=pi_color, ec=pi_color, linewidth=2)
ax.add_artist(arrow1)
ax.text(4.5, 7.8, 'HTTP POST', fontsize=9, ha='center', fontweight='bold')
ax.text(4.5, 7.2, 'JSON + Base64 Image', fontsize=8, ha='center')

# AI Services Section (Top)
ai_box = FancyBboxPatch((10, 7), 3.5, 2, 
                        boxstyle="round,pad=0.1", 
                        facecolor=ai_color, alpha=0.3, 
                        edgecolor=ai_color, linewidth=2)
ax.add_patch(ai_box)
ax.text(11.75, 8.5, 'AI Vision Services', 
        fontsize=12, fontweight='bold', ha='center')

# OpenAI box
openai_box = FancyBboxPatch((10.2, 7.8), 1.5, 0.5, 
                           boxstyle="round,pad=0.05", 
                           facecolor='white', edgecolor=ai_color)
ax.add_patch(openai_box)
ax.text(10.95, 8.05, 'OpenAI\nGPT-4V', fontsize=9, ha='center', fontweight='bold')

# Google box
google_box = FancyBboxPatch((11.8, 7.8), 1.5, 0.5, 
                           boxstyle="round,pad=0.05", 
                           facecolor='white', edgecolor=ai_color)
ax.add_patch(google_box)
ax.text(12.55, 8.05, 'Google\nGemini Pro', fontsize=9, ha='center', fontweight='bold')

ax.text(11.75, 7.4, 'Scene Analysis & Description', fontsize=9, ha='center')

# Arrow from Server to AI
arrow2 = ConnectionPatch((8.5, 8), (10, 8), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, 
                        mutation_scale=20, fc=ai_color, ec=ai_color, linewidth=2)
ax.add_artist(arrow2)
ax.text(9.25, 8.3, 'API Calls', fontsize=9, ha='center', fontweight='bold')

# Database Section (Bottom right)
db_box = FancyBboxPatch((10, 4), 3.5, 2, 
                        boxstyle="round,pad=0.1", 
                        facecolor=db_color, alpha=0.3, 
                        edgecolor=db_color, linewidth=2)
ax.add_patch(db_box)
ax.text(11.75, 5.5, 'SQLite Database', 
        fontsize=12, fontweight='bold', ha='center')
ax.text(11.75, 5.1, '(content_collection.db)', fontsize=10, ha='center', style='italic')

ax.text(11.75, 4.6, 'Storage Schema:', fontsize=10, ha='center', fontweight='bold')
ax.text(11.75, 4.2, '• Image (Base64)\n• Description (AI)\n• Timestamp\n• Device ID', 
        fontsize=9, ha='center', va='top')

# Arrow from Server to Database
arrow3 = ConnectionPatch((7.5, 6), (10.5, 5), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, 
                        mutation_scale=20, fc=db_color, ec=db_color, linewidth=2)
ax.add_artist(arrow3)
ax.text(8.8, 5.3, 'Data\nPersistence', fontsize=9, ha='center', fontweight='bold')

# Web Interface Section (Bottom left)
web_box = FancyBboxPatch((0.5, 2.5), 3.5, 2.5, 
                         boxstyle="round,pad=0.1", 
                         facecolor=web_color, alpha=0.3, 
                         edgecolor=web_color, linewidth=2)
ax.add_patch(web_box)
ax.text(2.25, 4.5, 'Web Interface', 
        fontsize=12, fontweight='bold', ha='center')

ax.text(2.25, 4.1, 'Browser-based UI:', fontsize=10, ha='center', fontweight='bold')
ax.text(2.25, 3.6, '• Content Management\n• Image Gallery\n• Date Filtering\n• Natural Language Queries', 
        fontsize=9, ha='center', va='top')

# Arrow from Web to Server
arrow4 = ConnectionPatch((4, 3.75), (5, 6.5), "data", "data",
                        arrowstyle="<->", shrinkA=5, shrinkB=5, 
                        mutation_scale=20, fc=web_color, ec=web_color, linewidth=2)
ax.add_artist(arrow4)
ax.text(4.2, 5, 'HTTP\nRequests', fontsize=9, ha='center', fontweight='bold', rotation=60)

# Query Processing Section (Bottom center)
query_box = FancyBboxPatch((5, 2.5), 3.5, 2.5, 
                          boxstyle="round,pad=0.1", 
                          facecolor='#E67E22', alpha=0.3, 
                          edgecolor='#E67E22', linewidth=2)
ax.add_patch(query_box)
ax.text(6.75, 4.5, 'Query Processing', 
        fontsize=12, fontweight='bold', ha='center')

ax.text(6.75, 4.1, 'Natural Language Search:', fontsize=10, ha='center', fontweight='bold')
ax.text(6.75, 3.6, '• GPT-4 Query Analysis\n• Semantic Matching\n• Time-based Filtering\n• Visual Results', 
        fontsize=9, ha='center', va='top')

# Configuration indicator
config_box = FancyBboxPatch((10, 1), 3.5, 1, 
                           boxstyle="round,pad=0.1", 
                           facecolor='#95A5A6', alpha=0.3, 
                           edgecolor='#95A5A6', linewidth=2)
ax.add_patch(config_box)
ax.text(11.75, 1.7, 'Configuration', 
        fontsize=12, fontweight='bold', ha='center')
ax.text(11.75, 1.3, 'config.json • API Keys • Settings', 
        fontsize=9, ha='center')

# Add some visual elements for data flow
ax.text(7, 0.5, 'Data Flow: Image Capture → AI Analysis → Database Storage → Web Query Interface', 
        fontsize=11, ha='center', fontweight='bold', style='italic')

# Add legend
legend_elements = [
    patches.Patch(color=pi_color, alpha=0.3, label='IoT Device Layer'),
    patches.Patch(color=server_color, alpha=0.3, label='Application Server'),
    patches.Patch(color=ai_color, alpha=0.3, label='AI Processing'),
    patches.Patch(color=db_color, alpha=0.3, label='Data Storage'),
    patches.Patch(color=web_color, alpha=0.3, label='User Interface')
]

ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0))

plt.tight_layout()
plt.savefig('/home/jerry/dev/mnemosyne/docs/assets/system-diagram.png', 
            dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()

print("System diagram generated successfully: docs/assets/system-diagram.png")