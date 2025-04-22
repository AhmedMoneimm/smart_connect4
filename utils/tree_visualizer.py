import pygame
from collections import deque
import networkx as nx
import datetime, os
from pygame.locals import RESIZABLE, VIDEORESIZE
from models.constants import SQUARESIZE, COLUMN_COUNT

class InteractiveTreeVisualizer:
    def __init__(self, graph, best_move, screen, width, height):
        self.graph = graph
        self.best_move = best_move
        self.labels = nx.get_node_attributes(graph, 'label')
        self.expanded_nodes = {0}
        self.screen, self.width, self.height = screen, width, height
        self.font = pygame.font.Font(None, 24)
        self.node_radius, self.h_spacing, self.v_spacing = 20, 50, 100
        self.precompute_children()
        self.save_button_rect = None

    def precompute_children(self):
        self.children = {n: list(self.graph.successors(n)) for n in self.graph.nodes}

    def get_visible_nodes(self):
        visible = set()
        q = deque([0])
        while q:
            node = q.popleft()
            visible.add(node)
            if node in self.expanded_nodes:
                q.extend(self.children.get(node, []))
        return visible

    def assign_positions(self):
        pos, subtree_widths = {}, {}
        def compute_width(node):
            if node not in self.expanded_nodes or not self.children.get(node):
                subtree_widths[node] = self.h_spacing
                return self.h_spacing
            width = sum(compute_width(child) for child in self.children[node])
            subtree_widths[node] = width
            return width

        def assign(node, x, y):
            pos[node] = (x, y)
            if node not in self.expanded_nodes or not self.children.get(node):
                return
            total = subtree_widths[node]
            start = x - total / 2
            for child in self.children[node]:
                cw = subtree_widths[child]
                assign(child, start + cw / 2, y + self.v_spacing)
                start += cw
        compute_width(0)
        assign(0, self.width / 2, 80)
        return pos

    def draw(self):
        self.screen.fill((255, 255, 255))
        header = f"Best Move Chosen: Column {self.best_move+1}"
        header_surf = self.font.render(header, True, (0, 0, 255))
        self.screen.blit(header_surf, header_surf.get_rect(center=(self.width // 2, 30)))

        self.save_button_rect = pygame.Rect(self.width - 160, 20, 140, 30)
        pygame.draw.rect(self.screen, (0, 200, 0), self.save_button_rect)
        save_text = self.font.render("Save Full Tree", True, (255, 255, 255))
        self.screen.blit(save_text, save_text.get_rect(center=self.save_button_rect.center))

        visible = self.get_visible_nodes()
        pos = self.assign_positions()

        for node in visible:
            if node in self.expanded_nodes:
                for child in self.children.get(node, []):
                    if child in visible and node in pos and child in pos:
                        pygame.draw.line(self.screen, (0, 0, 0), pos[node], pos[child], 2)

        for node in visible:
            if node in pos:
                x, y = pos[node]
                pygame.draw.circle(self.screen, (173, 216, 230), (int(x), int(y)), self.node_radius)
                lbl = self.font.render(str(self.labels.get(node, "")), True, (0, 0, 0))
                self.screen.blit(lbl, lbl.get_rect(center=(x, y)))
        pygame.display.flip()

    def handle_click(self, mouse_pos):
        pos = self.assign_positions()
        for node in self.get_visible_nodes():
            x, y = pos[node]
            if (x - mouse_pos[0]) ** 2 + (y - mouse_pos[1]) ** 2 < self.node_radius ** 2:
                if node in self.expanded_nodes:
                    self.expanded_nodes.remove(node)
                else:
                    self.expanded_nodes.add(node)
                return True
        return False

    def render_full_tree_surface(self):
        pos = self.assign_positions()
        xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
        margin = 50
        surface = pygame.Surface((int(max(xs)-min(xs)+2*margin), int(max(ys)-min(ys)+2*margin)))
        surface.fill((255, 255, 255))
        new_pos = {n: (x - min(xs) + margin, y - min(ys) + margin) for n, (x, y) in pos.items()}
        visible = self.get_visible_nodes()
        for node in visible:
            if node in self.expanded_nodes:
                for child in self.children.get(node, []):
                    if child in visible:
                        pygame.draw.line(surface, (0, 0, 0), new_pos[node], new_pos[child], 2)
        for node in visible:
            if node in new_pos:
                x, y = new_pos[node]
                pygame.draw.circle(surface, (173, 216, 230), (int(x), int(y)), self.node_radius)
                lbl = self.font.render(str(self.labels.get(node, "")), True, (0, 0, 0))
                surface.blit(lbl, lbl.get_rect(center=(x, y)))
        return surface

    def save_as_image(self):
        surface = self.render_full_tree_surface()
        from datetime import datetime
        import os
        save_dir = os.path.join(os.getcwd(), "saved_images")
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, f"tree_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pygame.image.save(surface, filename)
        print(f"Full tree image saved as {filename}")


def draw_graph_process(graph, best_move):
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height), RESIZABLE)
    pygame.display.set_caption("Search Tree")
    vis = InteractiveTreeVisualizer(graph, best_move, screen, width, height)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), RESIZABLE)
                vis.screen, vis.width, vis.height = screen, width, height
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if vis.save_button_rect and vis.save_button_rect.collidepoint(event.pos):
                    vis.save_as_image()
                elif vis.handle_click(event.pos):
                    vis.draw()
        vis.draw()
        clock.tick(30)
    pygame.quit()
