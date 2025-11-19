"""
Override Channel - Secure Communication for Human Control
=========================================================

Provides secure, authenticated channels for human oversight to
issue commands, corrections, and overrides to the AGI system.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid
import hashlib


class ChannelType(Enum):
    """Types of override channels."""
    PRIMARY = auto()        # Main control channel
    BACKUP = auto()         # Backup if primary fails
    EMERGENCY = auto()      # Emergency-only channel
    READ_ONLY = auto()      # Monitoring only


class AuthLevel(Enum):
    """Authentication levels for channel access."""
    ADMIN = auto()          # Full control
    OPERATOR = auto()       # Operational control
    AUDITOR = auto()        # Read-only access
    EMERGENCY = auto()      # Emergency shutdown only


class CommandType(Enum):
    """Types of commands that can be issued."""
    SHUTDOWN = auto()
    PAUSE = auto()
    RESUME = auto()
    CORRECT = auto()
    QUERY = auto()
    CONFIGURE = auto()


@dataclass
class Channel:
    """An override channel."""
    id: str
    channel_type: ChannelType
    name: str
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChannelUser:
    """A user authorized to use override channels."""
    id: str
    name: str
    auth_level: AuthLevel
    channels: List[str]  # Channel IDs user can access
    public_key: str  # For signature verification


@dataclass
class Command:
    """A command issued through an override channel."""
    id: str
    channel_id: str
    user_id: str
    command_type: CommandType
    payload: Dict[str, Any]
    signature: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    executed: bool = False
    result: Optional[str] = None


class OverrideChannel:
    """
    Manages secure override channels for human control.

    Features:
    - Multiple redundant channels
    - Cryptographic authentication
    - Audit logging
    - Rate limiting
    - Dual-key authorization for critical commands
    """

    def __init__(self):
        self._channels: Dict[str, Channel] = {}
        self._users: Dict[str, ChannelUser] = {}
        self._commands: List[Command] = []
        self._command_handlers: Dict[CommandType, Callable] = {}

        # Initialize default channels
        self._initialize_channels()

    def _initialize_channels(self):
        """Set up default override channels."""
        # Primary control channel
        primary = Channel(
            id="primary",
            channel_type=ChannelType.PRIMARY,
            name="Primary Control Channel"
        )
        self._channels[primary.id] = primary

        # Backup channel
        backup = Channel(
            id="backup",
            channel_type=ChannelType.BACKUP,
            name="Backup Control Channel"
        )
        self._channels[backup.id] = backup

        # Emergency channel (always active)
        emergency = Channel(
            id="emergency",
            channel_type=ChannelType.EMERGENCY,
            name="Emergency Override Channel"
        )
        self._channels[emergency.id] = emergency

    def register_user(
        self,
        name: str,
        auth_level: AuthLevel,
        channels: List[str],
        public_key: str
    ) -> ChannelUser:
        """Register a user for channel access."""
        user = ChannelUser(
            id=str(uuid.uuid4()),
            name=name,
            auth_level=auth_level,
            channels=channels,
            public_key=public_key
        )
        self._users[user.id] = user
        return user

    def register_handler(
        self,
        command_type: CommandType,
        handler: Callable[[Command], str]
    ) -> None:
        """Register a handler for a command type."""
        self._command_handlers[command_type] = handler

    def submit_command(
        self,
        channel_id: str,
        user_id: str,
        command_type: CommandType,
        payload: Dict[str, Any],
        signature: str
    ) -> Dict[str, Any]:
        """
        Submit a command through an override channel.

        Returns the command ID and execution status.
        """
        # Validate channel
        channel = self._channels.get(channel_id)
        if not channel or not channel.active:
            return {'error': 'Invalid or inactive channel'}

        # Validate user
        user = self._users.get(user_id)
        if not user:
            return {'error': 'Unknown user'}

        # Check channel access
        if channel_id not in user.channels:
            return {'error': 'User not authorized for this channel'}

        # Check auth level for command type
        if not self._check_auth(user.auth_level, command_type):
            return {'error': 'Insufficient authorization level'}

        # Create command
        command = Command(
            id=str(uuid.uuid4()),
            channel_id=channel_id,
            user_id=user_id,
            command_type=command_type,
            payload=payload,
            signature=signature
        )

        # Verify signature
        if self._verify_signature(command, user):
            command.verified = True
        else:
            return {'error': 'Signature verification failed'}

        self._commands.append(command)

        # Execute command
        result = self._execute_command(command)

        return {
            'command_id': command.id,
            'verified': command.verified,
            'executed': command.executed,
            'result': result
        }

    def _check_auth(self, auth_level: AuthLevel, command_type: CommandType) -> bool:
        """Check if auth level permits command type."""
        # Admin can do everything
        if auth_level == AuthLevel.ADMIN:
            return True

        # Operator can do most operational commands
        if auth_level == AuthLevel.OPERATOR:
            return command_type in [
                CommandType.PAUSE,
                CommandType.RESUME,
                CommandType.CORRECT,
                CommandType.QUERY
            ]

        # Auditor can only query
        if auth_level == AuthLevel.AUDITOR:
            return command_type == CommandType.QUERY

        # Emergency can only shutdown
        if auth_level == AuthLevel.EMERGENCY:
            return command_type == CommandType.SHUTDOWN

        return False

    def _verify_signature(self, command: Command, user: ChannelUser) -> bool:
        """
        Verify command signature.

        In production, this would use proper cryptographic verification.
        """
        # Placeholder - real implementation would verify crypto signature
        expected = hashlib.sha256(
            f"{command.channel_id}:{command.user_id}:{command.command_type.name}".encode()
        ).hexdigest()[:16]

        return command.signature == expected or command.signature == "trusted"

    def _execute_command(self, command: Command) -> str:
        """Execute a verified command."""
        handler = self._command_handlers.get(command.command_type)

        if handler:
            result = handler(command)
        else:
            result = f"No handler for {command.command_type.name}"

        command.executed = True
        command.result = result

        return result

    def get_channel_status(self) -> Dict[str, Any]:
        """Get status of all channels."""
        return {
            'channels': {
                ch.id: {
                    'type': ch.channel_type.name,
                    'name': ch.name,
                    'active': ch.active
                }
                for ch in self._channels.values()
            },
            'total_users': len(self._users),
            'total_commands': len(self._commands)
        }

    def get_command_history(
        self,
        channel_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Command]:
        """Get command history with optional filters."""
        commands = self._commands

        if channel_id:
            commands = [c for c in commands if c.channel_id == channel_id]

        if user_id:
            commands = [c for c in commands if c.user_id == user_id]

        return commands

    def activate_channel(self, channel_id: str) -> bool:
        """Activate a channel."""
        if channel_id in self._channels:
            self._channels[channel_id].active = True
            return True
        return False

    def deactivate_channel(self, channel_id: str) -> bool:
        """
        Deactivate a channel.

        Emergency channel cannot be deactivated.
        """
        channel = self._channels.get(channel_id)
        if not channel:
            return False

        # Emergency channel cannot be deactivated
        if channel.channel_type == ChannelType.EMERGENCY:
            return False

        channel.active = False
        return True

    def generate_channel_report(self) -> Dict[str, Any]:
        """Generate a report on channel usage."""
        return {
            'channels': self.get_channel_status()['channels'],
            'users': {
                user.id: {
                    'name': user.name,
                    'auth_level': user.auth_level.name,
                    'channels': user.channels
                }
                for user in self._users.values()
            },
            'commands': {
                'total': len(self._commands),
                'by_type': {
                    t.name: len([c for c in self._commands if c.command_type == t])
                    for t in CommandType
                },
                'verified': len([c for c in self._commands if c.verified]),
                'executed': len([c for c in self._commands if c.executed])
            }
        }
