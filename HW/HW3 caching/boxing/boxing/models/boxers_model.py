import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from boxing.db import db
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Boxers(db.Model):
    """Represents a competitive boxer in the system.

    This model maps to the 'boxers' table in the database and stores personal
    and performance-related attributes such as name, weight, height, reach,
    age, and fight statistics. Used in a Flask-SQLAlchemy application to
    manage boxer data, run simulations, and track fight outcomes.

    """

    #CHANGE

    __tablename__ = 'Boxers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    reach = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    fights = db.Column(db.Integer, nullable=False, default=0)
    wins = db.Column(db.Integer, nullable=False, default=0)
    weight_class = db.Column(db.String)

    def validate(self) -> None:
        """Validates the boxer instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name must be a non-empty string.")
        if not isinstance(self.weight, float) or self.weight < 125:
            raise ValueError("Weight must be a non-empty string.")
        if not isinstance(self.height, float) or self.height <= 0:
            raise ValueError("Height must be an integer greater than 1900.")
        if not isinstance(self.reach, float) or self.reach <= 0:
            raise ValueError("Reach must be a non-empty string.")
        if not isinstance(self.age, int) or self.age < 18 or self.age > 40:
            raise ValueError("Age must be a positive integer.")


    #CHANGE
    def __init__(self, name: str, weight: float, height: float, reach: float, age: int):
        """Initialize a new Boxer instance with basic attributes.

        Args:
            name (str): The boxer's name. Must be unique.
            weight (float): The boxer's weight in pounds. Must be at least 125.
            height (float): The boxer's height in inches. Must be greater than 0.
            reach (float): The boxer's reach in inches. Must be greater than 0.
            age (int): The boxer's age. Must be between 18 and 40, inclusive.

        Notes:
            - The boxer's weight class is automatically assigned based on weight.
            - Fight statistics (`fights` and `wins`) are initialized to 0 by default in the database schema.

        """
        self.name = name
        self.weight = weight
        self.height = height
        self.reach = reach
        self.age = age
        self.fights = 0
        self.wins = 0
        self.weight_class = "s"

    @classmethod
    def get_weight_class(cls, weight: float) -> str:
        """Determine the weight class based on weight.

        This method is defined as a class method rather than a static method,
        even though it does not currently require access to the class object.
        Both @staticmethod and @classmethod would be valid choices in this context;
        however, using @classmethod makes it easier to support subclass-specific
        behavior or logic overrides in the future.

        Args:
            weight: The weight of the boxer.

        Returns:
            str: The weight class of the boxer.

        Raises:
            ValueError: If the weight is less than 125.

        """
        pass

    @classmethod
    def create_boxer(cls, name: str, weight: float, height: float, reach: float, age: int) -> None:
        """Create and persist a new Boxer instance.

        Args:
            name: The name of the boxer.
            weight: The weight of the boxer.
            height: The height of the boxer.
            reach: The reach of the boxer.
            age: The age of the boxer.

        Raises:
            IntegrityError: If a boxer with the same name already exists.
            ValueError: If the weight is less than 125 or if any of the input parameters are invalid.
            SQLAlchemyError: If there is a database error during creation.

        """
        logger.info(f"Creating boxer: {name}, {weight=} {height=} {reach=} {age=}")

        try:
            boxer = Boxers(
                    name=name.strip(),
                    weight=weight,
                    height=height,
                    reach=reach,
                    age=age
            )
            boxer.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise
        try:
            # Check for existing boxer with same compound key (artist, title, year)
            existing = Boxers.query.filter_by(name=name.strip(), weight=weight, height=height).first()
            if existing:
                logger.error(f"Boxer already exists: {name} - {weight} ({height})")
                raise ValueError(f"Boxer with name '{name}', weight '{weight}', and height {height} already exists.")

            db.session.add(boxer)
            db.session.commit()
            logger.info(f"Boxer created successfully: {name}")
        except IntegrityError:
            logger.error(f"Boxer with name '{name}' already exists.")
            db.session.rollback()
            raise ValueError(f"Song with artist '{name}', title '{weight}', and year {height} already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during creation: {e}")
            raise

    @classmethod
    def get_boxer_by_id(cls, boxer_id: int) -> "Boxers":
        """Retrieve a boxer by ID.

        Args:
            boxer_id: The ID of the boxer.

        Returns:
            Boxer: The boxer instance.

        Raises:
            ValueError: If the boxer with the given ID does not exist.

        """
        try:
            boxer = cls.query.get(boxer_id)
            if boxer is None:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError("Value Error")
            logger.info(f"Successfully retrieved song: {boxer.name} - {boxer.weight} ({boxer.height})")
            return boxer
        
        except:
            logger.error(f"Database error while retrieving song by ID {boxer.id}: {e}")
            raise


    #CHANGE
    @classmethod
    def get_boxer_by_name(cls, name: str) -> "Boxers":
        """Retrieve a boxer by name.

        Args:
            name: The name of the boxer.

        Returns:
            Boxer: The boxer instance.

        Raises:
            ValueError: If the boxer with the given name does not exist.

        """
        try:
            boxer = cls.query.get(name=name.strip())
            if boxer is None:
                logger.info(f"Boxer '{name}' not found.")
                raise ValueError(f"Song with ID {name} not found")
            
            logger.info(f"Successfully retrieved song: {boxer.name} - {boxer.weight} ({boxer.height})")
            return boxer

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving song by ID {name}: {e}")
            raise

    #CHANGE
    @classmethod
    def delete(cls, boxer_id: int) -> None:
        """Delete a boxer by ID.

        Args:
            boxer_id: The ID of the boxer to delete.

        Raises:
            ValueError: If the boxer with the given ID does not exist.

        """
        try:
            boxer = cls.get_boxer_by_id(boxer_id)
            if boxer is None:
                logger.info(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")
            db.session.delete(boxer)
            db.session.commit()
            logger.info(f"Boxer with ID {boxer_id} permanently deleted.")
        
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting boxer with ID {boxer_id}: {e}")
            db.session.rollback()
            raise

    #CHANGE
    def update_stats(self, result: str) -> None:
        """Update the boxer's fight and win count based on result.

        Args:
            result: The result of the fight ('win' or 'loss').

        Raises:
            ValueError: If the result is not 'win' or 'loss'.
            ValueError: If the number of wins exceeds the number of fights.

        """
        try:
            if result not in {"win", "loss"}:
                raise ValueError("Result must be 'win' or 'loss'.")

            self.fights += 1
            if result == "win":
                self.wins += 1

            if self.wins > self.fights:
                raise ValueError("Wins cannot exceed number of fights.")

            db.session.commit()
            logger.info(f"Updated stats for boxer {self.name}: {self.fights} fights, {self.wins} wins.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating win count for boxer with ID {self.id}: {e}")
            db.session.rollback()
            raise

    @staticmethod
    def get_leaderboard(sort_by: str = "wins") -> List[dict]:
        """Retrieve a sorted leaderboard of boxers.

        Args:
            sort_by (str): Either "wins" or "win_pct".

        Returns:
            List[Dict]: List of boxers with stats and win percentage.

        Raises:
            ValueError: If the sort_by parameter is not valid.

        """
        logger.info(f"Retrieving leaderboard. Sort by: {sort_by}")

        if sort_by not in {"wins", "win_pct"}:
            logger.error(f"Invalid sort_by parameter: {sort_by}")
            raise ValueError(f"Invalid sort_by parameter: {sort_by}")

        boxers = Boxers.query.filter(Boxers.fights > 0).all()

        def compute_win_pct(b: Boxers) -> float:
            return round((b.wins / b.fights) * 100, 1) if b.fights > 0 else 0.0

        leaderboard = [{
            "id": b.id,
            "name": b.name,
            "weight": b.weight,
            "height": b.height,
            "reach": b.reach,
            "age": b.age,
            "weight_class": b.weight_class,
            "fights": b.fights,
            "wins": b.wins,
            "win_pct": compute_win_pct(b)
        } for b in boxers]

        leaderboard.sort(key=lambda b: b[sort_by], reverse=True)
        logger.info("Leaderboard retrieved successfully.")
        return leaderboard

    
