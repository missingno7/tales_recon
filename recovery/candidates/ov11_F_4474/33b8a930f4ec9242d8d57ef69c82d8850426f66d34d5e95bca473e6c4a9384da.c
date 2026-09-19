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
extern char G_h01_9C2C;
extern int F_h00_57D2();

recovered(action,state)
int action;
struct State *state;
{
    if (state->countdown > 0)
        state->countdown--;
    else {
        state->index++;
        if (state->index < state->limit) {
            if (state->counter)
                state->counter += 16;
        }
        switch (action) {
        case 27:
            if (state->action && state->index >= state->limit) {
                state->index = 0;
                state->limit = 4;
                state->counter = &G_h01_9F0C;
            }
            break;
        case 36:
            action = state->action;
            goto again;
        case 1:
            if (state->index >= state->limit) {
                state->index = 0;
                state->limit = 1;
                state->counter = &G_h01_9C2C;
                F_h00_57D2(94);
            } else if (state->index == 3)
                F_h00_57D2(87);
            break;
        case 3:
            if (state->action && state->index >= state->limit) {
                state->index = 0;
                state->limit = 4;
                state->counter = &G_h01_9F0C;
            }
            break;
        }
again:
        if (state->index < state->limit && state->counter)
            state->countdown = ((struct Counter *)state->counter)->value;
    }
}
