Asset: assets/human-machine.png. Created with the built-in image-generation tool.

Prompt: Transparent monochrome charcoal stippling / engraving artwork inspired by The Creation of Adam. A natural anatomical human hand reaches from the left; a clearly mechanical hand with segmented metal fingers, knuckle bearings, cables and panel seams reaches from the right. Both index fingers point toward one another. Long forearms extend to the frame edges. No text, labels, UI, or other objects.

The frontend samples the source anatomy into stable individual dots. The displayed scene renders those dots directly, without sketch lines or bitmap textures. Both hands start visibly separated, with fingertips around one-third and two-thirds of the desktop window. Each scroll pose articulates both index fingers at two joints, curls and releases the other fingers through separate joint influences, and rotates both wrists. A continuous flex-and-release motion accompanies the approach. At the final position the fingertips meet and the forearms remain anchored at the screen edges. Scrolling up reverses the entire gesture. There are no mobile-specific layouts.

Run the local preview with `node server.cjs` and open http://127.0.0.1:4173/.
