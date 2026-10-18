extern int arc_stream_buffer_position;
extern char *arc_stream_buffer_cursor;
extern long arc_file;
extern char archive_read_buffer[1024];
extern long Read();
extern int report_loader_error();

char
recovered()
{
    long amount;

    if (++arc_stream_buffer_position >= 1024) {
        amount = Read(arc_file, archive_read_buffer, 1024L);
        if (amount <= 0)
            report_loader_error(8000);
        arc_stream_buffer_position = 0;
        arc_stream_buffer_cursor = archive_read_buffer;
    } else
        ++arc_stream_buffer_cursor;
    return *arc_stream_buffer_cursor;
}
