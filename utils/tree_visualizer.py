import pygame
from collections import deque
import networkx as nx
import os, datetime

from pygame.locals import (
    FULLSCREEN, RESIZABLE, VIDEORESIZE, MOUSEWHEEL,
    KEYDOWN, K_f, K_LEFT, K_RIGHT, K_UP, K_DOWN
)

class InteractiveTreeVisualizer:
    def __init__(self, graph, best_move, screen, width, height):
        self.graph = graph
        self.best_move = best_move
        self.labels = nx.get_node_attributes(graph, 'label')
        self.types = nx.get_node_attributes(graph, 'node_type')
        self.expanded_nodes = {0}
        self.screen, self.width, self.height = screen, width, height
        self.font = pygame.font.Font(None, 24)
        self.node_radius = 20
        self.h_spacing = 50
        self.v_spacing = 100

        self.offset = [0, 0]
        self.pan_speed = 50

        self.precompute_children()
        self.precompute_sizes()
        self.save_button_rect = None

    def precompute_children(self):
        self.children = {n: list(self.graph.successors(n)) for n in self.graph.nodes}

    def precompute_sizes(self):
        self.text_sizes = {n: self.font.size(str(lbl)) for n, lbl in self.labels.items()}
        default = self.font.size("0")
        self.node_dims = {}
        for n in self.graph.nodes:
            w, h = self.text_sizes.get(n, default)
            w += 10; h += 6
            w = max(w, 2*self.node_radius)
            h = max(h, 2*self.node_radius)
            self.node_dims[n] = (w, h)

    def get_visible_nodes(self):
        vis, q = set(), deque([0])
        while q:
            n = q.popleft()
            vis.add(n)
            if n in self.expanded_nodes:
                q.extend(self.children.get(n, []))
        return vis

    def compute_widths(self):
        widths = {}
        def dfs(n):
            if n not in self.expanded_nodes or not self.children.get(n):
                w, _ = self.node_dims.get(n, (self.h_spacing, 2*self.node_radius))
                widths[n] = w
                return w
            total = sum(dfs(c) for c in self.children[n])
            total += max(0, (len(self.children[n]) - 1) * self.h_spacing)
            widths[n] = total
            return total
        dfs(0)
        return widths

    def assign_positions(self):
        widths = self.compute_widths()
        pos = {}
        total_w = widths.get(0, self.width)
        margin = self.h_spacing
        root_x = (self.width/2 if self.width >= total_w + 2*margin
                  else margin + total_w/2)

        def dfs(n, x, y):
            pos[n] = (x, y)
            if n not in self.expanded_nodes or not self.children.get(n):
                return
            start = x - widths[n]/2
            for c in self.children[n]:
                cw = widths[c]
                dfs(c, start + cw/2, y + self.v_spacing)
                start += cw + self.h_spacing

        dfs(0, root_x, 80)
        return pos

    def draw(self):
        self.screen.fill((255, 255, 255))

        # Header & Save button
        hdr = self.font.render(f"Best Move: Col {self.best_move+1}", True, (0, 0, 255))
        self.screen.blit(hdr, hdr.get_rect(center=(self.width//2, 30)))
        self.save_button_rect = pygame.Rect(self.width-160, 20, 140, 30)
        pygame.draw.rect(self.screen, (0, 200, 0), self.save_button_rect)
        btn = self.font.render("Save Full Tree", True, (255, 255, 255))
        self.screen.blit(btn, btn.get_rect(center=self.save_button_rect.center))

        # Compute & pan positions
        self.precompute_children(); self.precompute_sizes()
        vis = self.get_visible_nodes()
        raw_pos = self.assign_positions()
        pos = {n: (raw_pos[n][0] + self.offset[0],
                   raw_pos[n][1] + self.offset[1])
               for n in raw_pos}

        # Draw edges
        for n in vis:
            if n in self.expanded_nodes:
                for c in self.children.get(n, []):
                    if c in vis:
                        pygame.draw.line(self.screen, (0,0,0),
                                         pos[n], pos[c], 2)

        # Draw nodes
        lh = self.font.get_linesize()
        for n in vis:
            x, y = pos[n]
            w, h = self.node_dims.get(n, (2*self.node_radius,2*self.node_radius))
            rect = pygame.Rect(int(x-w/2), int(y-h/2), int(w), int(h))
            if self.types.get(n)=='chance':
                pygame.draw.rect(self.screen, (255,215,0), rect)
            else:
                pygame.draw.ellipse(self.screen, (173,216,230), rect)

            lines = str(self.labels.get(n,'')).split('\n')
            total_h = len(lines)*lh
            start_y = y - total_h/2 + lh/2
            for i, ln in enumerate(lines):
                txt = self.font.render(ln, True, (0,0,0))
                self.screen.blit(txt, txt.get_rect(center=(x, start_y + i*lh)))

        pygame.display.flip()

    def handle_click(self, mouse_pos):
        # convert click to tree coordinates
        raw_click = (mouse_pos[0] - self.offset[0],
                     mouse_pos[1] - self.offset[1])
        raw_pos = self.assign_positions()
        for n in self.get_visible_nodes():
            x, y = raw_pos[n]
            w, h = self.node_dims.get(n, (2*self.node_radius,2*self.node_radius))
            if (x - raw_click[0])**2 + (y - raw_click[1])**2 < (max(w,h)/2)**2:
                if n in self.expanded_nodes:
                    self.expanded_nodes.remove(n)
                else:
                    self.expanded_nodes.add(n)
                return True
        return False

    def render_full_tree_surface(self):
        # fully draw all visible nodes/edges on a big surface
        pos = self.assign_positions()
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        m = 50
        surf_w = int(max(xs) - min(xs) + 2*m)
        surf_h = int(max(ys) - min(ys) + 2*m)
        surf = pygame.Surface((surf_w, surf_h))
        surf.fill((255,255,255))

        off_min = (min(xs), min(ys))
        new_pos = {
            n: (pos[n][0] - off_min[0] + m,
                pos[n][1] - off_min[1] + m)
            for n in pos
        }
        vis = self.get_visible_nodes()

        # edges
        for n in vis:
            if n in self.expanded_nodes:
                for c in self.children.get(n, []):
                    if c in vis:
                        pygame.draw.line(surf, (0,0,0),
                                         new_pos[n], new_pos[c], 2)

        # nodes
        lh = self.font.get_linesize()
        for n in vis:
            x, y = new_pos[n]
            w, h = self.node_dims.get(n, (2*self.node_radius,2*self.node_radius))
            rect = pygame.Rect(int(x-w/2), int(y-h/2), int(w), int(h))
            if self.types.get(n)=='chance':
                pygame.draw.rect(surf, (255,215,0), rect)
            else:
                pygame.draw.ellipse(surf, (173,216,230), rect)

            lines = str(self.labels.get(n,'')).split('\n')
            total_h = len(lines)*lh
            start_y = y - total_h/2 + lh/2
            for i, ln in enumerate(lines):
                txt = self.font.render(ln, True, (0,0,0))
                surf.blit(txt, txt.get_rect(center=(x, start_y + i*lh)))

        return surf

    def save_as_image(self):
        surf = self.render_full_tree_surface()
        d = os.path.join(os.getcwd(), 'saved_images')
        os.makedirs(d, exist_ok=True)
        fname = os.path.join(d, f"tree_vis_{datetime.datetime.now():%Y%m%d_%H%M%S}.png")
        pygame.image.save(surf, fname)
        print(f"Saved: {fname}")


def draw_graph_process(graph, best_move):
    pygame.init()
    width, height = 1200, 800
    fullscreen = False
    screen = pygame.display.set_mode((width, height), RESIZABLE)
    pygame.display.set_caption("Search Tree")

    vis = InteractiveTreeVisualizer(graph, best_move, screen, width, height)
    clock = pygame.time.Clock()

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == KEYDOWN:
                if ev.key == K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0,0), FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1200,800), RESIZABLE)
                    vis.screen = screen
                    vis.width, vis.height = screen.get_size()

                elif ev.key == K_LEFT:
                    vis.offset[0] += vis.pan_speed
                elif ev.key == K_RIGHT:
                    vis.offset[0] -= vis.pan_speed
                elif ev.key == K_UP:
                    vis.offset[1] += vis.pan_speed
                elif ev.key == K_DOWN:
                    vis.offset[1] -= vis.pan_speed

            elif ev.type == VIDEORESIZE:
                width, height = ev.size
                screen = pygame.display.set_mode((width, height), RESIZABLE)
                vis.screen, vis.width, vis.height = screen, width, height

            elif ev.type == MOUSEWHEEL:
                vis.offset[0] += ev.x * vis.pan_speed
                vis.offset[1] += ev.y * vis.pan_speed

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if vis.save_button_rect and vis.save_button_rect.collidepoint(ev.pos):
                    vis.save_as_image()
                elif vis.handle_click(ev.pos):
                    vis.draw()

        vis.draw()
        clock.tick(30)

    pygame.quit()
