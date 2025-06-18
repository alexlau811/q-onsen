"""
Staff module for the Onsen Resort Management Game.
This module handles the creation and management of staff members.
"""

import random

class Staff:
    """Base class for all staff members."""
    
    def __init__(self, name, role, skill_level):
        self.name = name
        self.role = role
        self.skill_level = skill_level  # 1-10 scale
        self.happiness = 80  # 0-100 scale
        self.salary = self._calculate_salary()
        self.days_worked = 0
    
    def _calculate_salary(self):
        """Calculate the staff member's salary based on role and skill level."""
        base_salary = {
            "Manager": 5000,
            "Receptionist": 3000,
            "Attendant": 2500,
            "Cleaner": 2000,
            "Chef": 4000,
            "Server": 2200,
            "Maintenance": 3500,
            "Security": 3000
        }
        
        # If role not in dictionary, use a default value
        base = base_salary.get(self.role, 2500)
        
        # Adjust for skill level - exponential increase for higher skills
        # Level 1: base salary
        # Level 2: base + 30%
        # Level 3: base + 70%
        # Level 4: base + 120%
        # Level 5: base + 200%
        # Level 6: base + 300%
        # Level 7: base + 420%
        # Level 8: base + 560%
        # Level 9: base + 720%
        # Level 10: base + 900%
        skill_multipliers = [0, 0.3, 0.7, 1.2, 2.0, 3.0, 4.2, 5.6, 7.2, 9.0]
        
        # Cap skill level to available multipliers
        capped_skill = min(self.skill_level, len(skill_multipliers))
        return base * (1 + skill_multipliers[capped_skill - 1])
    
    def work(self):
        """Simulate the staff member working for a day."""
        self.days_worked += 1
        
        # Happiness decreases slightly each day
        self.happiness = max(0, self.happiness - random.randint(0, 2))
        
        # Every 30 days, consider a raise or skill improvement
        if self.days_worked % 30 == 0:
            if random.random() < 0.3:  # 30% chance
                self.skill_level = min(5, self.skill_level + 1)
                self.salary = self._calculate_salary()
    
    def give_bonus(self, amount):
        """Give a bonus to increase happiness."""
        self.happiness = min(100, self.happiness + amount // 100)
    
    def __str__(self):
        """String representation of the staff member."""
        skill_stars = "★" * self.skill_level + "☆" * (5 - self.skill_level)
        return (f"{self.name} - {self.role}\n"
                f"Skill: {skill_stars}\n"
                f"Happiness: {self.happiness}/100\n"
                f"Salary: ¥{int(self.salary)}/day\n"
                f"Days Worked: {self.days_worked}")


class StaffManager:
    """Class to manage all staff members."""
    
    def __init__(self):
        self.staff = []
        self.available_candidates = []
        self._generate_candidates(5)  # Start with 5 candidates
    
    def hire(self, candidate_index):
        """Hire a candidate from the available pool."""
        if 0 <= candidate_index < len(self.available_candidates):
            new_staff = self.available_candidates.pop(candidate_index)
            self.staff.append(new_staff)
            return new_staff
        return None
    
    def fire(self, staff_index):
        """Fire a staff member."""
        if 0 <= staff_index < len(self.staff):
            fired_staff = self.staff.pop(staff_index)
            return fired_staff
        return None
    
    def _generate_candidates(self, count):
        """Generate a number of candidates for hiring."""
        first_names = ["Takashi", "Yuki", "Haruka", "Kenji", "Akira", "Yumi", 
                      "Satoshi", "Emi", "Hiroshi", "Naomi", "Kazuki", "Ayumi"]
        last_names = ["Tanaka", "Suzuki", "Sato", "Watanabe", "Ito", "Yamamoto", 
                     "Nakamura", "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki"]
        
        roles = ["Manager", "Receptionist", "Attendant", "Cleaner", 
                "Chef", "Server", "Maintenance", "Security"]
        
        for _ in range(count):
            name = f"{random.choice(last_names)} {random.choice(first_names)}"
            role = random.choice(roles)
            skill_level = random.randint(1, 5)
            
            self.available_candidates.append(Staff(name, role, skill_level))
    
    def refresh_candidates(self):
        """Refresh the list of available candidates."""
        self.available_candidates = []
        self._generate_candidates(random.randint(3, 7))
    
    def get_total_salary(self):
        """Calculate the total daily salary for all staff."""
        return sum(staff.salary for staff in self.staff)
    
    def work_day(self):
        """Process a work day for all staff."""
        for staff in self.staff:
            staff.work()
            
            # Random events
            if random.random() < 0.05:  # 5% chance
                event_type = random.random()
                if event_type < 0.4:  # 40% of events are positive
                    staff.happiness = min(100, staff.happiness + random.randint(5, 15))
                else:  # 60% of events are negative
                    staff.happiness = max(0, staff.happiness - random.randint(5, 15))
    
    def get_average_happiness(self):
        """Calculate the average happiness of all staff."""
        if not self.staff:
            return 0
        return sum(staff.happiness for staff in self.staff) / len(self.staff)
    
    def get_staff_by_role(self, role):
        """Get all staff members with a specific role."""
        return [staff for staff in self.staff if staff.role == role]
        
    def get_average_skill(self):
        """Calculate the average skill level of all staff."""
        if not self.staff:
            return 0
        return sum(staff.skill_level for staff in self.staff) / len(self.staff)
