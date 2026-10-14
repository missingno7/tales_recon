/* Independent naturally allocated link harness. */
extern int recovered();
int (*candidate_reference)() = recovered;
main() { return 0; }
struct Record { int ignored; int value1; int value2; int value3; int value4; int value5; int value6; };
struct ClusterRecord {
    char pad0[8];
    int value8;
    int value10;
    char pad12[2];
    int value14;
    int value16;
    char pad18[12];
    int state30;
    int value32;
    char pad34[6];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};
struct Target { int x; int y; };
struct Descriptor { long object; int word4; int type; int word8; int word10; int dy; int dx; };
struct Controller { int x; int y; char f4[48]; char state; };
struct Object { char f0[52]; char state; };
struct Header { int count; char *data; };
struct LongSlot { long value; long pad[3]; };
struct DrawRecord {
    int x;
    int y;
    char unused[48];
    char pen;
};
struct Record__v2 {
    int field0;
    char unused0[22];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char unused1[28];
};
struct Slot { long value; char unused[12]; };
struct MotionRecord {
    char pad0[2];
    char motion[28];
    short v30;
    short v32;
    short pad34;
    short v36;
    short v38;
    short v40;
    short v42;
    short state;
    char remainder[18];
};
struct Row { int field0; int field2; int field4; };
struct Record__v3 {
    int field0;
    char gap2[6];
    int field8;
    char gap10[14];
    int field24;
    int field26;
    int field28;
    int field30;
    int field32;
    int field34;
    char gap36[8];
    int field44;
    int field46;
    int field48;
    int field50;
    int field52;
    char gap54[2];
    int field56;
    int field58;
    int field60;
    int field62;
};
struct TableCell {
    int value;
    char unused[12];
};
struct Object__v2 {
    char pad0[46];
    int active;
    int pad1;
    int x;
    int y;
    int old_x;
    int previous_x;
    int old_y;
    int previous_y;
    char pad2[2];
};
struct Controller__v2 {
    int x;
    int y;
    char pad[48];
    char state;
};
struct Record__v4 { int pad[23]; int state; int gap; int x,y; char tail[10]; };
struct Object__v3 {
    char pad00[0x1e];
    int value1e;
    int value20;
    char pad24[10];
    int state2c;
    int gate2e;
    int state30;
    int y32;
    int x34;
    char pad36[2];
    int value38;
    char pad3a[2];
    int value3c;
    char pad3e[2];
};
struct Record__v5 {
    char unused0[4];
    int value1;
    int value2;
    char unused1[10];
    int value3;
    char unused2[12];
};
struct Event {
    char pad0[2];
    int value2;
    char pad4[2];
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad18[6];
    int value18;
    int value1a;
    char rest[4];
};
struct Event__v2 {
    char pad0[2];
    int value2;
    int value4;
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    char pad12[2];
    int work14;
    int work16;
    int work18;
    int work1a;
    int count1c;
    int value1e;
};
struct Sprite { int x,y; char pad4[48]; char value34; };
struct Event__v3 {
    char pad0[2];
    int value2;
    int value4;
    int kind;
    int value8;
    int value10;
    int value12;
    int value14;
    int value16;
    int value18;
    int value1a;
    char rest[10];
};
struct Event__v4 {
    char pad0[4];
    int value4;
    char pad6[2];
    int value8;
    char padA[2];
    int valueC;
    int valueE;
    char tail[16];
};
struct Record__v6 { int state; char tail[30]; };
struct Record__v7 {
    char pad0[12];
    int value12;
    int value14;
    char pad2[6];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};
struct Record__v8 {
    char pad0[22];
    int value22;
    char pad1[2];
    int value26;
    int state;
    int value30;
};
struct Row__v2 {
	short word0;
	short word2;
	short unused4[4];
	short word12;
	short word14;
	short unused16[8];
};
struct State {
    int value0;
    int value2;
    int unused4;
    int value6;
    int value8;
    int code;
    int unusedc;
    int unusede;
    char *address;
    int value14;
};
struct Target__v2 {
    char padding[6];
    int value6;
};
struct Counter {
    char pad[6];
    int value;
};
struct State__v2 {
    char pad0[6];
    int index;
    int countdown;
    int limit;
    char pad1[4];
    char *counter;
    int action;
};
struct Target__v3 {
    int x;
    int y;
    char pad[48];
    char state;
};
struct Holder {
    struct Target *target;
    char pad0;
    char state;
    char pad1[6];
    int x;
    int y;
};
struct Motion {
    int x;
    int y;
    char pad[8];
    int remaining;
    int active;
    struct Holder *holder;
};
struct Rect {
    int kind;
    int x;
    int y;
    int width;
    int height;
    int index;
    char pad[2];
};
struct Record__v9 {
    int value;
    char rest[12];
};
struct Destination { char pad[52]; char value; };
struct Source {
    struct Destination *destination;
    char pad0;
    char value;
    int delay;
    char pad1[4];
    int x;
    int y;
};
struct Descriptor__v2 { long object; char pad4; char state; int type; char pad8[4]; int dy; int dx; };
struct Object__v4 { char pad[52]; char state; };
struct AnimRecord {
    char prefix[22];
    int animation;
    int flags;
    int x;
    int y;
    int row;
    int column;
    int value;
    int extra;
    int tail;
};
struct Record__v10 {
    char unused[24];
    int value24;
    int value26;
    int value28;
    int value30;
    int value32;
    int value34;
    int value36;
    int value38;
};
struct MotionRecord__v2 {
    char bytes[40];
};
struct ScreenRecord {
    char prefix[12];
    int slot0c;
    char reserved0e[8];
    int mode;
    int frame;
    int x;
    int y;
    int row;
    int column;
    int id;
    int flags;
    int tail;
};
struct Record__v11 {
	char pad0[12];
	int state;
	int value;
	char pad10[10];
	int x;
	int y;
	char gap[4];
	int first;
	int second;
	int third;
};
struct GridRecord {
    char prefix[8];
    int code;
    int state;
    char pad12[0x1c];
    int duration;
    int counter;
    int vertical;
    int horizontal;
    char tail[4];
};
struct MotionRecord__v3 {
    char pad[18];
    char motion;
    char remainder[33];
};
struct Record__v12 { int fields[15]; int value; char tail[20]; };
struct ClusterRecord__v2 {
    int value0;
    int value2;
    char pad4[14];
    char pad18[26];
    int value2c;
    int value2e;
    int state30;
    int value32;
};
struct InitRecord { char prefix[0x2c]; int value2c; int value2e; int value30; int value32; };
struct Record__v13 { int field0,value; char tail[48]; };
struct ClusterRecord__v3 {
    char f0[8];
    int value8;
    int value10;
    char f12[2];
    int value14;
    int value16;
    char f18[12];
    int state30;
    int value32;
    int *ref34;
    char f38[2];
    int state40;
    int value42;
    int value2c;
    int value2e;
    char tail[4];
};
struct ARecord { int value0; int value2; int value4; int value6; };
struct BRecord {
    int value0; int value2; int value4; int value6; int value8;
    int value10; int value12; int value14; int value16;
    char padding[26]; int value44; int value46; int unused48; int unused50;
};
struct MotionRecord__v4 {
    char pad[10];
    char motion;
    char remainder[29];
};
struct MotionRecord__v5 {
    char prefix[32];
    int field20;
    int field22;
    int field24;
    int field26;
};
struct Item {
    int value0;
    int value2;
    char pad4[6];
    int value10;
    char pad12[20];
    int state;
    int value34;
    int value36;
    char pad38[2];
};
struct Record__v14 { int head[2],field4,field6,middle[7],state,value,extra[3],field32,x,y,last; };
struct Record__v15 {
    int field0;
    int field2;
    char unused[30];
    int field34;
    int field36;
    char unused2[2];
};
struct Display {
    long value0;
    int value4;
    int value6;
    char padding[8];
};
struct Record__v16 {
    int input0;
    int input2;
    char padding0[28];
    int value20;
    int value22;
    int value24;
    int value26;
};
struct Record__v17 {
    int unused0, unused2;
    int left, right, top, bottom;
    int initial_x, initial_y, offset_y;
    int x, y, flags;
    int unused24, unused26, unused28;
    int step, active;
};
struct VRecord {
    int field0;
    int field2;
    char unused0[8];
    int field12;
    int field14;
    int field16;
    char unused1[6];
    int field24;
    int field26;
    int field28;
    char unused2[4];
};
struct Record__v18 {
    char pad0[4];
    int first;
    int first_old;
    int second;
    int second_old;
    int x;
    int y;
    int pad_between;
    int x2;
    int y2;
    char pad1[9];
    char state;
    char pad2[2];
};
struct Record__v19 { int pad[6]; int a,b,gap,c,d; char tail[12]; };
struct DistanceRecord {
    char pad0[18];
    int value18;
    int value20;
    char tail[12];
};
struct InitRecord__v2 { int value0; int value2; int value4; int value6; int pad8; };
struct Target__v4 { char pad0[52]; char value52; };
struct Record__v20 {
    int unused0;
    int unused1;
    int first;
    int second;
    int count;
};
struct Output {
    int first;
    int second;
};
struct Record__v21 {
    int value;
    int value2;
    int value4;
    int value6;
    char tail[2];
};
struct Record__v22 { int value; char tail[8]; };
struct Record__v23 {
    int field0;
    int field2;
    char unused[6];
};
int G_h01_12FE;
long G_h01_2C26;
char G_h01_2C2C;
long G_h01_46CA;
long G_h01_46CE;
long G_h01_46D2;
char *G_h01_46D6;
long G_h01_46DA;
int G_h01_7A94;
int G_h01_8A3C;
int G_h01_8A3E;
int G_h01_8A42;
struct Record G_h01_8A66[1];
int G_h01_8B1C[41][4];
short G_h01_940C[1];
int G_h01_94AC;
int G_h01_94AE;
int G_h01_94B8;
int G_h01_94BA;
int G_h01_94BC;
int G_h01_94E6;
long G_h01_9FA6;
char G_h01_16E6[1];
int F_h00_0FDE() { return 0; }
int F_h00_2816() { return 0; }
int F_h00_307C() { return 0; }
int F_h00_31AA() { return 0; }
int F_h00_330E() { return 0; }
int F_h00_435E() { return 0; }
int F_h00_4D04() { return 0; }
int F_h00_4EC6() { return 0; }
int F_h00_57D2() { return 0; }
int F_h00_868C() { return 0; }
int F_h00_86A8() { return 0; }
int F_h00_8A46() { return 0; }
int F_h00_8BC8() { return 0; }
long G_h01_9F4E;
long G_h01_9F52;
long G_h01_9F56;
long G_h01_9F5E;
long G_h01_9F62;
long G_h01_9F66;
long G_h01_9F6A;
long G_h01_9F6E;
long G_h01_9F76;
long G_h01_9F7E;
long G_h01_9F82;
long G_h01_9F8A;
long G_h01_9F8E;
long G_h01_9F92;
long G_h01_9F96;
long G_h01_9F9A;
long G_h01_9F9E;
long G_h01_9FA2;
int F_h00_3BD2() { return 0; }
int G_h01_8A44;
int G_h01_8A48;
int G_h01_8A4A;
int G_h01_94BE;
int G_h01_1300[16];
struct ClusterRecord G_h01_8BEC[1];
int G_h01_945C[1];
int G_h01_94B0;
int G_h01_94B4;
int G_h01_94B6;
int G_h01_94C0;
int G_h01_94D6;
int G_h01_94D8;
int G_h01_7A90;
int G_h01_34D8[16];
int F_h00_4376() { return 0; }
int G_h01_94D4;
long G_h01_46E6;
char G_h01_94B3;
char *G_h01_94DA;
int G_h01_94DE;
int G_h01_94E0;
int G_h01_94C2;
int G_h01_94C4;
int G_h01_94C6;
int G_h01_94C8;
long G_h01_94CA;
long G_h01_94CE;
int F_h00_34E0() { return 0; }
int G_h01_1708;
int G_h01_170A;
int G_h01_170C;
int G_h01_170E;
int G_h01_94B2;
int F_h00_30F0() { return 0; }
struct Header *G_h01_7A96;
char G_h01_7A9A[1];
int G_h01_8A3A;
int G_h01_8A40;
long G_h01_9F5A;
struct Descriptor G_h01_94EC[10];
struct Descriptor G_h01_958C[10];
struct Descriptor G_h01_962C[8];
struct Descriptor G_h01_96AC[8];
struct Descriptor G_h01_972C[3];
struct Descriptor G_h01_975C[3];
struct Descriptor G_h01_978C[7];
struct Descriptor G_h01_97FC[7];
struct Descriptor G_h01_986C[5];
struct Descriptor G_h01_98BC[9];
struct Descriptor G_h01_99DC[2];
struct Descriptor G_h01_99FC[2];
struct Descriptor G_h01_9A1C[5];
struct Descriptor G_h01_9A6C[5];
struct Descriptor G_h01_9ABC[3];
struct Descriptor G_h01_9AEC[1];
struct Descriptor G_h01_9AFC[5];
struct Descriptor G_h01_9B4C[7];
struct Descriptor G_h01_9BBC[7];
struct Descriptor G_h01_9C2C[6];
long F_h00_86DC() { return 0; }
long F_h00_291E() { return 0; }
int F_h00_3674() { return 0; }
int F_h00_3C0E() { return 0; }
long F_h00_75D8() { return 0; }
int F_h00_704E() { return 0; }
struct LongSlot G_h01_9F0C[4];
int G_h01_9F10;
int G_h01_9F20;
int G_h01_9F30;
int G_h01_9F40;
int G_h01_9F4C;
int G_h01_9FC0;
int G_h01_9FC2;
int G_h01_9FCC;
char G_h01_46E0;
int G_h01_9FAA;
int G_h01_9FC4;
int G_h01_9FC6;
int G_h01_9FC8;
int G_h01_9FCA;
int G_h01_9FAC;
int G_h01_9FB6;
char *G_h01_5370;
int F_h00_8B88() { return 0; }
int F_h00_8B4C() { return 0; }
int F_h00_8AA8() { return 0; }
char G_h01_46E1;
int F_h00_09C0() { return 0; }
void F_h00_8B76() { }
char G_h01_9D2C[1];
char G_h01_9D4C[1];
char G_h01_9D6C[1];
char G_h01_9D9C[1];
char G_h01_9E5C[1];
struct Record__v2 G_h01_9FCE[1];
int G_h01_9D30;
int G_h01_9D40;
int G_h01_9D4A;
int G_h01_9D50;
int G_h01_9D5A;
int G_h01_9D60;
int G_h01_9D6A;
int G_h01_9D70;
int G_h01_9D72;
int G_h01_9D80;
int G_h01_9D82;
int G_h01_9D90;
int G_h01_9DA0;
int G_h01_9DB0;
int G_h01_9DB2;
int G_h01_9DC0;
int G_h01_9DD0;
int G_h01_9DD2;
int G_h01_9DE0;
int G_h01_9DF0;
int G_h01_9DF2;
int G_h01_9E00;
int G_h01_9E10;
int G_h01_9E12;
int G_h01_9E20;
int G_h01_9E30;
int G_h01_9E32;
int G_h01_9E40;
int G_h01_9E50;
int G_h01_9E52;
int G_h01_9E60;
int G_h01_9E62;
int G_h01_9E70;
int G_h01_9E72;
int G_h01_9E80;
int G_h01_9E82;
int G_h01_9E90;
int G_h01_9E92;
int G_h01_9EA0;
int G_h01_9EA2;
struct Row G_h01_12C0[32];
int G_h01_7A92;
int G_h01_A14E;
unsigned int F_h00_463E() { return 0; }
struct TableCell G_h01_8A68[1];
int G_h01_A152;
struct Record__v5 G_h01_A15E[1];
int G_h01_A150;
int G_h01_A158;
int G_h01_A15A;
int G_h01_A154;
struct Record__v6 G_h01_A16A[36];
short G_h01_A156;
char G_h01_9CBC[1];
char G_h01_9CFC[1];
char G_h01_9CEC[1];
char G_h01_9EBC[1];
char G_h01_9EAC[1];
char G_h01_9D3C[1];
struct Rect G_h01_34EC[40];
long G_h01_A460;
int G_h01_8A6E[1];
int G_h01_A45E;
long F_h00_3B16() { return 0; }
int F_h00_3B84() { return 0; }
int G_h01_94E4;
struct Source *G_h01_94E8;
struct Descriptor__v2 G_h01_987C[1];
struct Descriptor__v2 G_h01_994C[1];
struct AnimRecord G_h01_3724[1];
char G_h01_9C8C[1];
char G_h01_9C92[1];
char G_h01_9CC2[1];
int G_h01_9C90;
int G_h01_9CA0;
int G_h01_9CB0;
int G_h01_9CC0;
int G_h01_9CD0;
int G_h01_9CE0;
int G_h01_9CF0;
int G_h01_9D00;
int G_h01_9D10;
int G_h01_9D20;
int G_h01_371C;
int G_h01_371E;
int G_h01_3720;
int G_h01_3722;
int G_h01_00A8;
int G_h01_00CC;
int G_h01_8A6A[1];
int G_h01_37F2;
int G_h01_37EC;
int G_h01_37F4[40];
int G_h01_3844[40];
int G_h01_37EE;
int G_h01_37F0;
struct MotionRecord__v4 G_h01_A464[1];
int G_h01_9EB0;
int G_h01_9EC0;
int G_h01_9EC2;
int G_h01_9ED0;
int G_h01_9ED2;
int G_h01_9EE0;
int G_h01_9EE2;
int G_h01_9EF0;
int G_h01_9EF2;
int G_h01_9F00;
int G_h01_9F02;
struct Record__v17 G_h01_A554[10];
struct InitRecord__v2 G_h01_A6A8[1];
struct Record__v22 G_h01_A6B0[36];
int G_h01_1322[64];
int G_h01_13A2[64];
/* Runtime helper link control (harness only). */
helper_export_control(a,b,c,d)
long a,b;
unsigned long c,d;
{
    float f, g;
    int k;

    f = f + g;
    if (f < g) k = 1;
    f = f / g;
    k = f;
    f = k;
    f = f * g;
    f = -f;
    f = f - g;
    if (f) k = 2;
    return 0;
}
