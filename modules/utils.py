#!/usr/bin/env python3
'''This module contains utility functions used by other modules.
They do not depend on the bot framework.'''

import datetime
import inspect
import tempfile
from collections import defaultdict
import pygments
from pygments.lexers import IrcLogsLexer
from pygments.formatters import HtmlFormatter
import boto3

def from_admin_channel_only(func):
    '''Only calls the decorated function if called from an administration channel.'''
    sig = inspect.signature(func)

    def decorator(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        sender = bound_args.arguments['trigger'].sender
        admin_channels = bound_args.arguments['bot'].config.banlogger.admin_channels
        if sender in admin_channels:
            func(*args, **kwargs)
    return decorator

def create_s3_paste(s3_bucket_name, paste_content, wanted_title=None):
    '''Creates a paste and returns the link to the formatted version'''
    if wanted_title:
        file_title = wanted_title
    else:
        file_title = create_timestamp_file_name()

    filename_text = file_title + '.txt'
    filename_formatted = file_title + '.html'

    paste_formatted = pygments.highlight(paste_content,
                                         IrcLogsLexer(),
                                         HtmlFormatter(full=True,
                                                       style='monokai'))

    filelike_text = tempfile.TemporaryFile()
    filelike_text.write(paste_content.encode('utf-8'))
    filelike_text.seek(0)

    filelike_formatted = tempfile.TemporaryFile()
    filelike_formatted.write(paste_formatted.encode('utf-8'))
    filelike_formatted.seek(0)

    s3client = boto3.client('s3')
    s3resource = boto3.resource('s3')
    s3client.upload_fileobj(filelike_text, s3_bucket_name, filename_text)
    s3client.upload_fileobj(filelike_formatted,
                            s3_bucket_name,
                            filename_formatted)

    # Set the content-type, it cannot be done at upload time it seems...
    obj_text = s3resource.Object(s3_bucket_name, filename_text)
    obj_text.copy_from(CopySource={'Bucket': s3_bucket_name,
                                   'Key': filename_text},
                       MetadataDirective='REPLACE',
                       ContentType='text/plain; charset=utf-8')
    obj_formatted = s3resource.Object(s3_bucket_name, filename_formatted)
    obj_formatted.copy_from(CopySource={'Bucket': s3_bucket_name,
                                        'Key': filename_formatted},
                            MetadataDirective='REPLACE',
                            ContentType='text/html; charset=utf-8')

    # Make the url to return
    url = 'http://{}/{}'.format(s3_bucket_name, filename_formatted)
    return url


def create_timestamp_file_name():
    '''Creates a filename based on ISO8601 using UTC'''
    current_time = datetime.datetime.now()
    iso_str = current_time.replace(microsecond=0).isoformat()+'z'
    file_title = iso_str.replace(':', '').replace('.', '').replace('-', '')
    return file_title
