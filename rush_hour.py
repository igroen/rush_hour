import argparse
import csv
import logging
import time
from collections import deque, namedtuple
from enum import Enum
from functools import partial
from pprint import pformat

BOARD_SIZE = 6
EMPTY_CELL = " "

Direction = Enum("Direction", ["HORIZONTAL", "VERTICAL"])
Car = namedtuple("Car", ["name", "x", "y", "size", "direction"])

# Solution
ENDPOINT = Car(name="r", x=2, y=4, size=2, direction=Direction.HORIZONTAL)


def get_board(cars):
    """Return a Rush Hour board."""

    board = [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for car in cars:
        if car.direction is Direction.HORIZONTAL:
            for i in range(car.size):
                board[car.x][car.y + i] = car.name
        elif car.direction is Direction.VERTICAL:
            for i in range(car.size):
                board[car.x + i][car.y] = car.name
        else:
            raise ValueError()

    return board


def update_cars_tuple(cars, index, new_car):
    """Replace car by index in cars tuple."""

    new_cars = list(cars)
    new_cars[index] = new_car

    return tuple(new_cars)


def possible_moves(cars):
    """Return an iterator with all possible moves for a Rush Hour board."""

    board = get_board(cars)
    for i, car in enumerate(cars):
        update_car = partial(update_cars_tuple, cars, i)

        if car.direction is Direction.HORIZONTAL:
            # Move right
            if (
                car.y + car.size < BOARD_SIZE
                and board[car.x][car.y + car.size] == EMPTY_CELL
            ):
                yield update_car(
                    Car(car.name, car.x, car.y + 1, car.size, car.direction)
                )
            # Move left
            if car.y > 0 and board[car.x][car.y - 1] == EMPTY_CELL:
                yield update_car(
                    Car(car.name, car.x, car.y - 1, car.size, car.direction)
                )
        elif car.direction is Direction.VERTICAL:
            # Move down
            if (
                car.x + car.size < BOARD_SIZE
                and board[car.x + car.size][car.y] == EMPTY_CELL
            ):
                yield update_car(
                    Car(car.name, car.x + 1, car.y, car.size, car.direction)
                )
            # Move up
            if car.x > 0 and board[car.x - 1][car.y] == EMPTY_CELL:
                yield update_car(
                    Car(car.name, car.x - 1, car.y, car.size, car.direction)
                )
        else:
            raise ValueError()


def print_moves(history):
    """Print steps to solution."""

    logging.info("Total number of steps: %d", len(history) - 1)
    for i in range(len(history) - 1):
        for car1, car2 in zip(history[i], history[i + 1]):
            if car1 != car2:
                if car1.x > car2.x:
                    logging.info("%s-Up", car1.name)
                if car1.x < car2.x:
                    logging.info("%s-Down", car1.name)
                if car1.y > car2.y:
                    logging.info("%s-Left", car1.name)
                if car1.y < car2.y:
                    logging.info("%s-Right", car1.name)


def run(initial_cars):
    """Get solution."""

    boards_seen = set()
    queue = deque()
    queue.appendleft((initial_cars, []))

    while queue:
        board, history = queue.pop()

        # Continue loop if the same board is already processed
        # This means there is a shorter route
        if board in boards_seen:
            continue

        boards_seen.add(board)

        # Keep track of previous moves
        history = history + [board]

        # Solution found
        if ENDPOINT in board:
            print_moves(history)
            logging.debug(pformat([get_board(cars) for cars in history]))
            break

        queue.extendleft((move, history) for move in possible_moves(board))


def read_setup(csv_file):
    """Read initial board setup from CSV file and set correct data types."""

    for car in map(Car._make, csv.reader(open(csv_file))):
        if car.direction == "H":
            direction = Direction.HORIZONTAL
        elif car.direction == "V":
            direction = Direction.VERTICAL
        else:
            raise ValueError()

        yield Car(
            name=car.name,
            x=int(car.x),
            y=int(car.y),
            size=int(car.size),
            direction=direction,
        )


def get_args():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_file", help="CSV file containing the initial setup of the Rush Hour board"
    )
    parser.add_argument(
        "-s",
        "--show-boards",
        help="Print all rush hous boards to solution",
        action="store_true",
    )
    return parser.parse_args()


def main():
    args = get_args()

    if args.show_boards:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(format="%(message)s", level=log_level)

    initial_cars = tuple(read_setup(args.csv_file))

    logging.info("Initial board:\n%s", pformat(get_board(initial_cars)))

    start_time = time.time()
    run(initial_cars)
    duration = (time.time() - start_time) * 1000

    logging.info(f"Finding a solution took {duration:.2f} ms")


if __name__ == "__main__":
    main()
