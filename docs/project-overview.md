# Reachy Home Assistant - Project Overview

## Vision

The Reachy Home Assistant is a household assistant designed for a family of four. It combines a physical robot presence (Reachy Mini) with a web application to help manage daily family life through natural interaction.

## Goals

1. **Personalized Assistance**: Recognize each family member and provide tailored help
2. **Proactive Support**: Anticipate needs based on schedules and patterns
3. **Natural Interaction**: Communicate through voice with personality
4. **Family Coordination**: Keep everyone informed about schedules and tasks
5. **Privacy First**: Keep family data local and secure

## Key Capabilities

### Recognition
- **Face Recognition**: Identify family members on sight using InsightFace
- **Voice Recognition**: Know who's speaking using pyannote speaker embeddings
- **Combined Confidence**: Use both modalities for reliable identification

### Speech
- **Wake Word**: Always-on listening for "Hey Reachy"
- **Speech-to-Text**: Local transcription using faster-whisper
- **Text-to-Speech**: Natural voice synthesis using Kokoro
- **Speaker ID**: Identify who's talking for personalized responses

### Conversation
- **Natural Dialogue**: Claude-powered conversational AI
- **Context Awareness**: Remember past conversations and preferences
- **Tool Use**: Execute actions (reminders, calendar queries, etc.)
- **Personality**: Warm, helpful, age-appropriate interactions

### Memory
- **Semantic Search**: Find relevant memories using vector similarity
- **Personalization**: Remember preferences and patterns per user
- **Observations**: Track notable events and behaviors
- **Temporal Awareness**: Weight recent memories higher

### Integration
- **Cozi Calendar**: Sync family schedules automatically
- **Reachy Mini**: Control robot expressions and movements
- **Web Dashboard**: View and manage schedules, tasks, chats

## User Experience

### Morning Routine
1. Reachy recognizes Patrick entering the kitchen
2. "Good morning, Patrick! You have a 9 AM standup and Nico has soccer practice at 4."
3. Patrick asks about the weather
4. Reachy provides forecast and suggests appropriate clothing for the kids

### After School
1. Kids arrive home, Reachy greets each by name
2. "Welcome home, Nico! How was school? Remember, you have a math worksheet due tomorrow."
3. Tracks homework completion
4. Reminds about chores at appropriate times

### Family Coordination
1. Parent asks Reachy to remind kids about dinner
2. Reachy announces dinner time with enthusiasm
3. Tracks who has responded/arrived
4. Reports back to parent

## Technical Architecture

See [Architecture Summary](architecture-summary.md) for detailed technical information.

## Privacy Principles

1. **Local First**: All data stored on local machine
2. **No Cloud Dependency**: Works without internet (except Claude API)
3. **Family Control**: Parents can view and manage all data
4. **Minimal External Sharing**: Only necessary API calls to Claude
5. **Secure Storage**: Encrypted backups, no plaintext passwords

## Current Status

This is the initial scaffolding phase. The repository structure is set up with placeholder modules ready for implementation.

### Phase 1: Foundation (Current)
- [x] Repository scaffolding
- [x] Architecture decisions documented
- [x] Placeholder modules created
- [ ] Database schema implementation
- [ ] Basic face/voice enrollment

### Phase 2: Core Features
- [ ] Wake word detection
- [ ] Speech-to-text pipeline
- [ ] Face recognition pipeline
- [ ] Basic conversation flow
- [ ] Text-to-speech output

### Phase 3: Intelligence
- [ ] Claude API integration
- [ ] Memory storage and retrieval
- [ ] Cozi calendar sync
- [ ] Proactive greetings

### Phase 4: Web Application
- [ ] React frontend scaffold
- [ ] API endpoints
- [ ] Real-time updates
- [ ] Mobile-friendly design

### Phase 5: Polish
- [ ] Reachy Mini integration
- [ ] Expression animations
- [ ] Edge case handling
- [ ] Performance optimization
