import heapq
import itertools
import pprint

class Wall(object):
    @property
    def grid_char(self):
        return "#"

class Open(object):
    @property
    def grid_char(self):
        return "."

WALL = Wall()
OPEN = Open()

def adjacent_squares(x, y):
    return [(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)]

def open_adjacent_squares(x, y, grid):
    return itertools.ifilter(
        lambda (x_, y_): grid[y_][x_] is OPEN,
        [(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)]
    )

def closest_target(source, targets, grid):
    x, y = source
    fringe = [(0, (y, x), None, ((y, x),))]
    seen = set()
    nearest_distance = None
    nearest = []

    while fringe:
        dist, (y, x), parent, this_path = heapq.heappop(fringe)
        #seen.add((y, x))

        if nearest_distance is not None and dist > nearest_distance:
            # Already found something closer. Don't bother.
            continue

        if (y, x) in targets:
            if nearest_distance is None:
                nearest_distance = dist
                nearest.append(((y, x), this_path))
            elif nearest_distance == dist:
                nearest.append(((y, x), this_path))
            # Cannot beat this distance by traveling through this target square.
            continue

        for (nextX, nextY) in open_adjacent_squares(x, y, grid):
            if (nextY, nextX) not in seen:
                seen.add((nextY, nextX))
                item = (dist + 1, (nextY, nextX), (y, x), this_path + ((nextY, nextX),))
                heapq.heappush(fringe, item)

    # min(nearest) is the first one in there, reading-order wise.

    if not nearest:
        return None, None

    return min(nearest)

class Player(object):
    def __init__(self, x, y, grid, attack_power):
        self.x = x
        self.y = y
        self.grid = grid
        self.hit_points = 200
        self.alive = True
        self.attack_power = attack_power

    def get_targets(self):
        return itertools.ifilter(
            lambda p: not isinstance(p, type(self)),
            iter_players(self.grid)
        )

    def attackable_targets(self):
        enemy_type = Goblin if isinstance(self, Elf) else Elf

        for x, y in adjacent_squares(self.x, self.y):
            if isinstance(self.grid[y][x], enemy_type):
                yield (self.grid[y][x].hit_points, (y, x))

    def play_turn(self):
        def iter_reachable_squares():
            for target in self.get_targets():
                for (x, y) in open_adjacent_squares(target.x, target.y, self.grid):
                    yield (y, x)

        had_enemies = any(self.get_targets())

        if len(list(self.attackable_targets())) == 0:
            # Need to move.
            in_range_squares = set(iter_reachable_squares())
            closest_in_range, path = closest_target(
                (self.x, self.y), in_range_squares, self.grid)

            # Take one step toward the closest.
            if closest_in_range is not None:
                self.move_to(path[1])

        attackable_targets = list(self.attackable_targets())

        if attackable_targets:
            health, targetPosition = min(attackable_targets)
            self.attack(targetPosition)

        return had_enemies

    def move_to(self, position):
        y, x = position
        assert self.grid[y][x] is OPEN
        self.grid[self.y][self.x] = OPEN
        self.grid[y][x] = self
        self.y = y
        self.x = x

    def attack(self, position):
        targetY, targetX = position
        target = self.grid[targetY][targetX]
        target.hit_points -= self.attack_power
        if target.hit_points <= 0:
            target.alive = False
            self.grid[targetY][targetX] = OPEN

    def __repr__(self):
        return "<{} @ {}>".format(type(self), (self.x, self.y))

class Goblin(Player):
    @property
    def grid_char(self):
        return "G"

class Elf(Player):
    @property
    def grid_char(self):
        return "E"

def debug_grid(grid):
    for line in grid:
        print "".join(item.grid_char for item in line)

def iter_players(grid, obj_type=Player):
    return itertools.ifilter(
        lambda p: isinstance(p, obj_type),
        itertools.chain.from_iterable(grid)
    )

def go():
    def play(elf_power):
        """
        Returns (winning player type, number of losses in winning type)
        """
        grid = []

        with open("advent15.txt", "r") as f:
            for y, line in enumerate(f):
                line = line.rstrip("\n")
                grid_line = []
                for x, char in enumerate(line):
                    if "#" == char:
                        grid_line.append(WALL)
                    elif "." == char:
                        grid_line.append(OPEN)
                    elif "G" == char:
                        grid_line.append(Goblin(x, y, grid, 3))
                    elif "E" == char:
                        grid_line.append(Elf(x, y, grid, elf_power))
                    else:
                        assert False
                else:
                    grid.append(grid_line)

        rounds_completed = 0
        elves_original = list(iter_players(grid, Elf))
        goblins_original = list(iter_players(grid, Goblin))

        while True:
            for player in list(iter_players(grid)):
                if player.alive:
                    had_enemies = player.play_turn()
                    if not had_enemies:
                        break
            else:
                rounds_completed += 1

            #print rounds_completed
            #debug_grid(grid)

            elves = list(iter_players(grid, Elf))
            goblins = list(iter_players(grid, Goblin))

            if not elves:
                return (
                    Goblin,
                    rounds_completed * sum(g.hit_points for g in goblins),
                    len(goblins_original) - len(goblins))
            elif not goblins:
                return (
                    Elf,
                    rounds_completed * sum(e.hit_points for e in elves),
                    len(elves_original) - len(elves))

    lo = 4
    hi = 1000

    # Binary search for minimal elf power where elves win without any dying.

    while lo < hi:
        trial = (lo + hi) // 2
        winner, outcome, winners_died = play(trial)
        print trial
        if winner is Elf and winners_died == 0:
            hi = trial
        else:
            lo = trial + 1

    print lo, outcome

if __name__ == "__main__":
    go()
