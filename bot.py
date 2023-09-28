from random import choice
from typing import List, Tuple

import numpy as np

from ...bot import Bot
from ...constants import Move, MOVE_VALUE_TO_DIRECTION
from ...snake import Snake


# grid size is x-axis, y-axis


def is_on_grid(pos: np.array, grid_size: Tuple[int, int]) -> bool:
    """
    Check if a position is still on the grid
    """
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(pos: np.array, snakes: List[Snake]) -> bool:
    """
    Check if a position is occupied by any of the snakes
    """
    for snake in snakes:
        if snake.collides(pos):
            return True
    return False


class ExampleBot(Bot):
    MYSELF, OTHER, CANDY, EMPTY = 1, 2, 3, 4

    @property
    def name(self):
        return 'Wolverine'

    @property
    def contributor(self):
        return 'Jeroen'

    def __init__(self, id: int, grid_size: Tuple[int, int]):
        self.id = id
        self.grid_size = grid_size

    def _insert_snake(self, snake: Snake, symbol: int):
        snake_position_iter = iter(snake)
        snake_length = len(snake)
        for x in range(snake_length):
            xy_coordinate = next(snake_position_iter)
            self.flattened_board[self._flatten(xy_coordinate)] = symbol

    def _insert_candy(self, candy: np.array):
        pass

    def determine_next_move(self, snake: Snake, other_snakes: List[Snake], candies: List[np.array]) -> Move:
        # flatten the grid into a 1-dimensional array
        self.flattened_board = self.grid_size[0] * self.grid_size[1] * [self.EMPTY]

        # flatten myself into the board
        self._insert_snake(snake, self.MYSELF)

        # flatten other snakes into the board
        for other_snake in other_snakes:
            self._insert_snake(other_snake, self.OTHER)

        # flatten candies into the board
        for candy in candies:
            self._insert_candy(candy)

        # now see where the head might move next
        next_head_coordinates_in_reach = self._get_valid_neighbors(self._flatten(self._head(snake)))

        # now remove the in-reach coordinates that are myself
        next_head_coordinates_in_reach = [flattened_xy_coordinate for flattened_xy_coordinate in next_head_coordinates_in_reach if not self._occupied_by_myself(flattened_xy_coordinate)]

        # now remove the in-reach coordinates that collide with other snakes
        next_head_coordinates_in_reach = [flattened_xy_coordinate for flattened_xy_coordinate in next_head_coordinates_in_reach if not self._occupied_by_other_snake(flattened_xy_coordinate)]

        # now see if any of the in-reach coordinates have a candy
        candy_coordinates_in_reach = [flattened_xy_coordinate for flattened_xy_coordinate in next_head_coordinates_in_reach if self._occupied_by_candy(flattened_xy_coordinate)]

        # prefer candy in-reach coordinate over next-head coordinate
        if len(candy_coordinates_in_reach) > 0:
            return self._to_move(snake, self._unflatten(candy_coordinates_in_reach[0]))

        # no interesting in-reach coordinates, figure out a global direction towards the nearest candy
        # TODO
        # Generate a (width*height)*(width*height) graph
        # where the column index is my flattened head coordinate (source vertex)
        # where the row index is the flattened other vertex coordinate (target vertex)
        # Initialize values to infinite, mark non-snake coordinates as distance 1
        # Find the shortest path from source vertex to each candy vertex and pick the closest one
        # Then determine the next step in the closest path
        # https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
        # https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
        if len(next_head_coordinates_in_reach) > 0:
            return self._to_move(snake, self._unflatten(next_head_coordinates_in_reach[0]))
        # hmm, no next move possible, then simply die
        return Move.DOWN

    def _head(self, snake: Snake):
        return snake[0]

    def _grid_width(self) -> int:
        return self.grid_size[0]

    def _grid_height(self) -> int:
        return self.grid_size[1]

    def _flatten(self, xy_coordinate) -> int:
        return (self._grid_width() * xy_coordinate[0]) + xy_coordinate[1]
    
    def _unflatten(self, flattened_xy_coordinate) -> Tuple[int, int]:
        return divmod(flattened_xy_coordinate, self._grid_width());

    def _is_on_board(self, xy_coordinate) -> bool:
        return xy_coordinate[0] % self._grid_width() == xy_coordinate[0] and xy_coordinate[1] % self._grid_height() == xy_coordinate[1]

    def _get_valid_neighbors(self, flattened_xy_coordinate) -> List[int]:
        x, y = self._unflatten(flattened_xy_coordinate)
        # RIGHT, LEFT, UP, DOWN
        possible_neighbors = ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
        return [self._flatten(n) for n in possible_neighbors if self._is_on_board(n)]

    def _occupied_by_myself(self, flattened_xy_coordinate) -> bool:
        return self.flattened_board[flattened_xy_coordinate] == self.MYSELF

    def _occupied_by_other_snake(self, flattened_xy_coordinate) -> bool:
        return self.flattened_board[flattened_xy_coordinate] == self.OTHER

    def _occupied_by_candy(self, flattened_xy_coordinate) -> bool:
        return self.flattened_board[flattened_xy_coordinate] == self.CANDY

    def _to_move(self, snake: Snake, next_xy_coordinate: Tuple[int, int]) -> Move:
        current_head_coordinate = self._head(snake)
        if current_head_coordinate[0] == next_xy_coordinate[0]:
            if current_head_coordinate[1] < next_xy_coordinate[1]:
                return Move.UP
            else:
                return Move.DOWN
        else:
            if current_head_coordinate[0] < next_xy_coordinate[0]:
                return Move.RIGHT
            else:
                return Move.LEFT