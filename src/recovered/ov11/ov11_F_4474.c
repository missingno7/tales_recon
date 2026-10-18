struct Counter {
    char pad[6];
    int value;
};

struct State {
    char pad0[6];
    int index;
    int countdown;
    int limit;
    char pad1[4];
    char *counter;
    int action;
};

extern char G_h01_9F0C;
extern char jg_platform_animation_descriptors;
extern int play_sound();

recovered(action,state)
int action;
struct State *state;
{
    if (state->countdown > 0)
        state->countdown--;
    else {
        state->index++;
        if (state->index < state->limit && state->counter)
            state->counter += 16;
        switch (action) {
        case 33:
            if (state->action && state->index >= state->limit) {
                state->index = 0;
                state->limit = 4;
                state->counter = &G_h01_9F0C;
            }
            break;
        case 24:
            switch (state->action) {
            case 1:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 1;
                    state->counter = &jg_platform_animation_descriptors;
                }
                break;
            case 3:
                if (state->index >= state->limit) {
                    state->index = 0;
                    state->limit = 6;
                    state->counter = &jg_platform_animation_descriptors;
                    play_sound(94);
                } else if (state->index == 3)
                    play_sound(87);
                break;
            }
            break;
        }
        if (state->index < state->limit && state->counter)
            state->countdown = ((struct Counter *)state->counter)->value;
    }
}
