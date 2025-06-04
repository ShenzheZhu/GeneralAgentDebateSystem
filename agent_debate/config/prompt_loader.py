import os
import yaml
from typing import Dict, Any, Optional, List, Union

class PromptLoader:
    """Prompt loader class for managing YAML configurations"""
    
    def __init__(self, config_path: Optional[str] = None, background_config: Optional[Union[Dict[str, str], Dict[str, Dict[str, str]], List[Dict[str, str]]]] = None):
        """
        Initialize prompt loader
        :param config_path: Path to custom YAML config file
        :param background_config: Background configuration(s)
            For single agent: Dict with {"category": "academic", "role": "professor"}
            For dual agent: Dict with role assignments
                Example: {
                    "solver": {"category": "professional", "role": "engineer"},
                    "critic": {"category": "academic", "role": "professor"}
                }
            For multi agent: List of background configs for each agent
                Example: [
                    {"category": "academic", "role": "professor"},
                    {"category": "creative", "role": "philosopher"},
                    {"category": "professional", "role": "engineer"}
                ]
        """
        self.config_dir = os.path.join(os.path.dirname(__file__), 'prompts')
        self.backgrounds_dir = os.path.join(os.path.dirname(__file__), 'backgrounds')
        self.custom_config_path = config_path
        self.background_config = background_config
        self.prompts = {}  # Will be loaded on demand
        self.backgrounds = {}  # Will be loaded on demand
        
    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load YAML file"""
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
            
    def _deep_update(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep update dictionary"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                base[key] = self._deep_update(base[key], value)
            else:
                base[key] = value
        return base
        
    def _load_background(self, config: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Load background description
        :param config: Optional specific background config to load
        """
        if not config:
            if not isinstance(self.background_config, dict) or "category" not in self.background_config:
                return None
            config = self.background_config
            
        category = config.get("category")
        role = config.get("role")
        
        if not category or not role:
            return None
            
        if category not in self.backgrounds:
            file_path = os.path.join(self.backgrounds_dir, f'{category}.yaml')
            self.backgrounds[category] = self._load_yaml(file_path)
            
        return self.backgrounds[category].get(role, {}).get("description")
        
    def _load_agent_prompts(self, agent_type: str, role: Optional[str] = None) -> Dict[str, Any]:
        """
        Load prompts for specific agent type
        :param agent_type: Type of agent (single_agent, dual_agent, multi_agent)
        :param role: Optional role for dual_agent (solver or critic)
        """
        # Load default prompts
        default_path = os.path.join(self.config_dir, f'{agent_type}.yaml')
        prompts = self._load_yaml(default_path)
        
        # Override with custom prompts if provided
        if self.custom_config_path and os.path.exists(self.custom_config_path):
            custom_prompts = self._load_yaml(self.custom_config_path)
            if agent_type in custom_prompts:
                prompts = self._deep_update(prompts, custom_prompts[agent_type])
                
        # Add background if provided
        if agent_type == "multi_agent":
            # For multi-agent, backgrounds are applied in get_multi_agent_prompts
            return prompts
        elif agent_type == "dual_agent":
            # For dual agent, we need to handle both roles
            if isinstance(self.background_config, dict):
                for agent_role in ["solver", "critic"]:
                    if agent_role in self.background_config and agent_role in prompts:
                        background = self._load_background(self.background_config[agent_role])
                        if background:
                            prompts[agent_role]["system"] = background + "\n\n" + prompts[agent_role]["system"]
        else:  # single_agent
            if isinstance(self.background_config, dict) and "category" in self.background_config:
                background = self._load_background()
                if background and "system" in prompts:
                    prompts["system"] = background + "\n\n" + prompts["system"]
                
        return prompts
        
    def get_single_agent_prompts(self) -> Dict[str, str]:
        """Get single agent prompts"""
        if 'single_agent' not in self.prompts:
            self.prompts['single_agent'] = self._load_agent_prompts('single_agent')
        return self.prompts['single_agent'].copy()
        
    def get_dual_agent_prompts(self, role: str) -> Dict[str, str]:
        """
        Get dual agent prompts for a specific role
        :param role: Must be either 'solver' or 'critic'
        :returns: Dictionary containing prompts for the specified role
        """
        if role not in ["solver", "critic"]:
            raise ValueError("Role must be either 'solver' or 'critic'")
            
        if 'dual_agent' not in self.prompts:
            self.prompts['dual_agent'] = self._load_agent_prompts('dual_agent')
            
        role_prompts = self.prompts['dual_agent'].get(role, {})
        if not role_prompts:
            raise ValueError(f"No prompts found for role '{role}' in dual agent configuration")
            
        return role_prompts.copy()
        
    def get_multi_agent_prompts(self, agent_index: Optional[int] = None) -> Dict[str, str]:
        """
        Get multi agent prompts
        :param agent_index: Optional index to get background for specific agent
        :returns: Dictionary containing prompts, optionally with background for specific agent
        :raises: ValueError if agent_index is out of range
        """
        if 'multi_agent' not in self.prompts:
            self.prompts['multi_agent'] = self._load_agent_prompts('multi_agent')
            
        prompts = self.prompts['multi_agent'].copy()
        
        # Apply specific background if agent_index is provided
        if agent_index is not None:
            if not isinstance(self.background_config, list):
                raise ValueError("Background config must be a list for multi-agent setup")
                
            if not (0 <= agent_index < len(self.background_config)):
                raise ValueError(f"Agent index {agent_index} is out of range. Must be between 0 and {len(self.background_config)-1}")
                
            background = self._load_background(self.background_config[agent_index])
            if background and "system" in prompts:
                prompts["system"] = background + "\n\n" + prompts["system"]
                    
        return prompts
        
    def list_available_backgrounds(self) -> Dict[str, List[str]]:
        """List all available background categories and roles"""
        backgrounds = {}
        for file in os.listdir(self.backgrounds_dir):
            if file.endswith('.yaml'):
                category = file[:-5]  # Remove .yaml extension
                file_path = os.path.join(self.backgrounds_dir, file)
                roles = list(self._load_yaml(file_path).keys())
                backgrounds[category] = roles
        return backgrounds
        
    def get_background_roles(self) -> Union[Dict[str, Dict[str, str]], List[Dict[str, str]], None]:
        """Get the current background role assignments"""
        return self.background_config
        
    @staticmethod
    def format_prompt(prompt: str, **kwargs) -> str:
        """Format prompt with provided arguments"""
        return prompt.format(**kwargs)
        
    def reload_prompts(self) -> None:
        """Reload prompts from files"""
        self.prompts = {}  # Clear cache to force reload
        self.backgrounds = {}  # Clear background cache
        
    def save_prompts(self, agent_type: str, prompts: Dict[str, Any], path: str) -> None:
        """Save prompts to a YAML file"""
        # Load existing prompts if file exists
        existing_prompts = self._load_yaml(path) if os.path.exists(path) else {}
        
        # Update prompts for specific agent type
        existing_prompts[agent_type] = prompts
        
        # Save to file
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(existing_prompts, f, allow_unicode=True, sort_keys=False)
            
    def get_all_prompts(self) -> Dict[str, Any]:
        """Get all prompts"""
        # Load all agent types if not already loaded
        for agent_type in ['single_agent', 'dual_agent', 'multi_agent']:
            if agent_type not in self.prompts:
                self.prompts[agent_type] = self._load_agent_prompts(agent_type)
        return self.prompts.copy()

    def validate_background_config(self) -> bool:
        """
        Validate the background configuration
        :returns: True if configuration is valid, False otherwise
        :raises: ValueError if configuration is invalid
        """
        if self.background_config is None:
            return True
            
        if isinstance(self.background_config, list):
            # Multi-agent configuration
            if not self.background_config:
                raise ValueError("Multi-agent background config list cannot be empty")
            for i, config in enumerate(self.background_config):
                if not isinstance(config, dict) or "category" not in config or "role" not in config:
                    raise ValueError(f"Invalid background config at index {i}")
        elif isinstance(self.background_config, dict):
            if "solver" in self.background_config or "critic" in self.background_config:
                # Dual-agent configuration
                for role in ["solver", "critic"]:
                    if role not in self.background_config:
                        raise ValueError(f"Missing {role} configuration in dual-agent setup")
                    config = self.background_config[role]
                    if not isinstance(config, dict) or "category" not in config or "role" not in config:
                        raise ValueError(f"Invalid {role} configuration in dual-agent setup")
            else:
                # Single-agent configuration
                if "category" not in self.background_config or "role" not in self.background_config:
                    raise ValueError("Invalid single-agent background config")
        else:
            raise ValueError("Invalid background config type")
            
        return True 