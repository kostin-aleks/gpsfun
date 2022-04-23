"""
utils
"""

import os
import sys
import subprocess


def convertvideo(sourcefile, targetfile, convert2size="320x240"):
    """
      http://blog.go4teams.com/?p=56

DRM - Daniel’s Random Mutterings
What I Read; What I Have Read; and stuff I pick up and drag along
« Pet Peeves In Grammar, #34
I was dugg! »
Video Blogging using Django and Flash(tm) Video (FLV)

I just added Flash-based (FLV) video blogging support to my Django-powered travel portal site, trogger.de. The whole process is surprisingly simple and straightforward and can be done entirely with free (FLOSS) tools.

The video publishing workflow consists of the following parts:

    * A Django model to store our video and associated information
    * An upload form where the user can upload a video
    * Converting the video into a format usable on the Web
    * Extracting additional details
    * Playing the video in the Web browser
    * Making the player a bit friendlier
    * Advanced features

Following this simple workflow, trogger.de allows users to write and submit a blog post. Once that’s submitted, the user can add one (!) video file to it. When later viewing the blog entry, the attached video is shown in the browser.
The Django model

The Django model for storing the video is rather straightforward. In addition to storing the Video (or, rather, a reference to the video file) in a FileField, I’ve added a reference to the blog submission with which the video is related (I use this to look up the video when browsing the blog). Here’s my model, VideoSubmission:

class VideoSubmission(models.Model):
    videoupload = models.FileField (upload_to='videoupload')
    relatedsubmission = models.ForeignKey(Submission, null=True)
    comment = models.CharField( maxlength=250, blank=True )
    flvfilename = models.CharField( maxlength=250, blank=True, null=True )

In addition to the video FileField itself, I’ve added a “flvfilename” field to store the name of the converted movie file (see below).
Uploading the video

Video uploading is done using a normal File upload form. In the view for the upload form, we need to add the FormFields for the file upload fields created by Django:

def v_addvideo(request, submissionid):
    manipulator=VideoSubmission.AddManipulator()
    form=FormWrapper(manipulator,{},{})
    params = {'userAccount':request.user,'form':form,}
    c = Context( request, params)
    t = loader.get_template('video/addvideo.html')
    sub = Submission.objects.get(pk=submissionid)
    params['submission'] = sub
    return HttpResponse( t.render( c ) )

Our addvideo.html is pretty much the simplest upload form imaginable:

<form action="/video/upload/" method="post" enctype="multipart/form-data">
<table>
    <input type="hidden" name="relatedsubmission_id" value="{{submission.id}}" />
    <tr valign="top">
      <td>Video hochladen:<br/>(Nur AVI und FLV werden akzeptiert)</td>
      <td>{{ form.videoupload}} {{ form.videoupload_file }}<br/>
      Kommentar: <input type="text" name="comment"   style="width:100%" maxlength="250">
      </td>
    </tr>
    <tr valign="top">
      <td> </td>
      <td><input type="submit" Value="Hochladen"/> </td>
    </tr>
</table>
</form>

I’ve added the related submission ID as a hidden field, so that this gets submitted back to the upload process and I can create a link between the video and the blog entry.
Converting the video for use in the site

The users are asked to upload AVI videos to the site, but we cannot play AVI videos directly in the browser (at least not in a browser-independent manner). A good way to publish videos for viewing in a browser is using FLV (Flash(tm) Video) format. This is what YouTube, Google Video and a whole host of other sites use. If it’s good enough for them, it’s good enough for me!
Converting to FLV

So, how to convert the AVI video the user uploaded to a usable FLV format? Luckily, the OSS package ffmpeg [2] provides this conversion functionality (plus a wide range of other video conversion features one of which we’ll come to later on). The good thing about ffmpeg is that it is controlled entirely from the command-line and can be run in headless environments — this is vital for using it on an application server. Most other FLV conversion tools were either for Windows or came with some form of Gnome or KDE gui which wouldn’t have worked on my hosted Linux box.

The basic command for converting a video into FLV format is (see [1] in resources):

ffmpeg -i [sourcefile.avi] -acodec mp3 -ar 22050 -ab 32 -f flv -s 320×240 [destfile.flv]
Adding FLV metadata

This command creates a simple FLV format file, containing the video and audio streams. In addition, FLV files need meta-information such as duration, frames, etc. FLV movie players use this information to calculate progress bar sliders and allow the user to fast-forward or reverse through the video. For reasons which I didn’t bother to research, ffmpeg does not add this information. But there is a package which can: flvtool2 (see [3]). Using this tool, we can add FLV meta-information with the following command:

flvtool2 -U [flvfile]

(Warning, Djangoists — flvtool2 is written in Ruby. Please check your religious language preferences at the door and pick them up as you leave. Thank you).
Adding a video thumbnail

Blog entries in trogger.de can include pictures uploaded by the users. One of these pictures is displayed as a small preview when showing the blog posting (e.g. in the blog overview, or in the list of the latest blog submissions). Wouldn’t it be nice if we could also add a thumbnail for a video submission, so that the blog’s reader can get a first idea of what to expect? I think it would. And, again, ffmpeg comes to the rescue.

ffmpeg can extract single frames from a video stream, storing them in still image format. The command for doing this is:


ffmpeg -y -i [videofile] -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320×240 [thumbnailimage.png]
Putting it all together

With these individual steps, it’s EASY to put together a video conversion function which kicks in once a user has uploaded a video file. Since we have the information which video the user uploaded with the form, we convert this video into FLV format, add metadata and create a thumbnail image:

def convertvideo (video):
    if video is None:
        return "Kein Video im Upload gefunden"
    filename = video.videoupload
    print "Konvertiere Quelldatei: %s" + filename
    if filename is None:
        return "Video mit unbekanntem Dateinamen"
    sourcefile = "%s%s" % (settings.MEDIA_ROOT,filename)
    flvfilename = "%s.flv" % video.id
    thumbnailfilename = "%svideos/flv/%s.png" % (settings.MEDIA_ROOT, video.id)
    targetfile = "%svideos/flv/%s" % (settings.MEDIA_ROOT, flvfilename)
    ffmpeg = "ffmpeg -i %s -acodec mp3 -ar 22050 -ab 32 -f flv -s 320x240 %s" % (sourcefile,  targetfile)
    grabimage = "ffmpeg -y -i %s -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320x240 %s " % (sourcefile, thumbnailfilename)
    flvtool = "flvtool2 -U %s" % targetfile
    print ("Source : %s" % sourcefile)
    print ("Target : %s" % targetfile)
    print ("FFMPEG: %s" % ffmpeg)
    print ("FLVTOOL: %s" % flvtool)
    try:
        ffmpegresult = commands.getoutput(ffmpeg)
        print "-------------------- FFMPEG ------------------"
        print ffmpegresult
        # Check if file exists and is > 0 Bytes
        try:
            s = os.stat(targetfile)
            print s
            fsize = s.st_size
            if (fsize == 0):
                print "File is 0 Bytes gross"
                os.remove(targetfile)
                return ffmpegresult
            print "Dateigroesse ist %i" % fsize
        except:
            print sys.exc_info()
            print "File %s scheint nicht zu existieren" % targetfile
            return ffmpegresult
        flvresult = commands.getoutput(flvtool)
        print "-------------------- FLVTOOL ------------------"
        print flvresult
        grab = commands.getoutput(grabimage)
        print "-------------------- GRAB IMAGE ------------------"
        print grab
    except:
        print sys.exc_info()
        return sys.exc_info[1]
    video.flvfilename = flvfilename
    video.save()
    return None

Things to note

I’m keeping the media diectory for the uploads and the media directory for the converted results separate. This way, I can later on easily clear the upload area if I decide I don’t need the source videos any more (after all, they eat up valuable hosting space), without having to bother about accidentally deleting the converted data. Yes, I’m sometimes stupid in breathtakingly dumb ways. Also I can exclude the source video files from the daily backup.

If something goes wrong with the conversion, I return the output message from the conversion tool and actually display this in the Web page, so the user can see if there was a problem. I’m not too sure this is a good idea, yet. ffmpeg puts pathnames into its output, so the error message is exposing potentially exploitable information about the directory setup of my server. You might want to consider replacing path names before dumping the output message.

The converted video file is created in a subdirectory of the media root and has the VideoSubmission model instance’s ID as a filename (35.flv). This will always be unique, so there’s no need to think about another unique naming scheme. The PNG image thumbnail also has the ID as a filename, but with a PNG extension (duh!).
Playing the video in the Web browser

Now that the video was uploaded and (hopefully) successfully converted, we need to provide a way of viewing it. For this, I use an FLV player component called FlowPlayer, avilable as a SourceForge project [4]. The FlowPlayer SWF is embedded into the page and parameters are provided based on information from the video. In the blog entry view, I look for a related video submission which I pass in the context as “video”. The view template populates the SWF parameters using information from the “video” instance:

{% if video %}
<div style="textalign:center; width:100%;">
<center>
<object  type="application/x-shockwave-flash"
width="320" height="263" id="FlowPlayer" data="/showvideo/FlowPlayer.swf">
    <param name="allowScriptAccess" value="sameDomain" />
    <param name="movie" value="/showvideo/FlowPlayer.swf" />
    <param name="quality" value="high" />
    <param name="scale" value="noScale" />
    <param name="wmode" value="transparent" />
    <param name="flashvars" value="baseURL=/showvideo&videoFile=flv/{{video.flvfilename}}&autoPlay=false&bufferLength=5&loop=false&progressBarColor1=0xAAAAAA&progressBarColor2=0x555555&autoBuffering=false&splashImageFile=clicktoplay.jpg&hideControls=false" />
<p>Dein Browser scheint kein Flash-Plugin installiert zu haben</p>
</object>
<p>
<center>
<strong>{{video.comment}}</strong>
</center>
</p>
</center>
</div>
{% endif %}

Note the inconspicuous “splashImageFile=clicktoplay.jpg” hidden in the jumble of FLV parameters. FlowPlayer provides a very simple way of specifying a “splash screen” image which is displayed in place of the video until the user clicks on the Flash player to view the video. I’ve created a trogger-themed splash screen and use this for all embedded video submissions:

FlowPlayer splash screen
The end result

Thew end result is shown in the screenshot. A user-written blog entry, with an attached video which is played in the browser. Not bad for one day’s work, if I say so myself.


Manta Video in trogger page
Conversion quality and size issues

Quality of the converted FLV videos is pretty good, even at lower resolutions. Of course, YMMV or you may have other expectations. Using the conversion commands shown above, a 2.6MB camera movie was converted into an FLV file of 590kB. Depending on your intended use of the video (full-screen presentation?), and depending on how much bandwidth you want to burn, you may want to fiddle with some quality and compression parameters in ffmpeg.
Housekeeping

It is definitely a good idea to make sure that the FLV files are not actually served by Django, but directly by Apache (or even by another http server altogether). To serve the video files directly from Apache, we can exclude the video location “showvideo” from processing by Django by adding a section to the httpd.conf:

Alias /showvideo/ "/path/to/my/media/root/video/"
<Location "/showvideo/">
    SetHandler none
</Location>

Also, we should consider limiting the size of uploads, since we don’t want to drown in uploaded video (and we don’t want to get out-of-memory errors from Django, which holds the entires file upload in memory at least temporarily). As has been pointed out by Malcolm Tredinnick in the django-users group, this can be achieved using the LimitRequestBody directive.
Open Issues

One issue that I haven’t been able to solve is adequate support for more video formats. Windows Media stuff provides so many proprietary formats, codecs, etc., that it’s hard even for a project such as ffmpeg to keep up. As a result, I’ve limited video upload to AVI files, and make it quite clear to the uploader that potentially the video he’s uploading cannot be used, due to format problems. AVI videos captured by my digital camera (such as the diving video in the screenshot) can be converted quite well. As soon as somebody recodes the video, converts it to WMV, there’s trouble (even more so if the video contains any Digital Restrictions Management). There are loads of forum entries in the Net discussing potential solutions. Since they all involved hacking additional (sometimes binary) codes into ffmpeg, I wasn’t adventurous enough to try them.

If anyone can point me at a reliable way of converting (unprotected) WMV files and other video formats into FLV format, I would be very grateful.

I discovered that MPlayer can also be used for such conversions and can also be run in a headless environment; since conversion with ffmpeg worked, I didn’t do any more experiments — maybe someone else can enlighten me as to wether MPlayer would actually be better or cope with more formats?

Also, I’m doing the video conversion in-line with the browser upload. This is OK for shorter videos, where I can make the user wait for a result. For larger video submissions it might be useful to decouple the video processing and do it in a separate thread, updating the blog entry when finished.
Resources

[1] ffmpeg
http://ffmpeg.mplayerhq.hu/

[3] flvtool2
http://rubyforge.org/projects/flvtool2/

[4] FlowPlayer
http://flowplayer.sourceforge.net/

Tags: Django; Python; FLV; video; trogger

P.S. You can check out a blog entry with video submission in my trogger blog at http://www.trogger.de/blog/8/60/mit-mantas-tauchen-vor-machchafushi/fullentry/.

Bookmark on del.icio.us
Add this post to digg.com
Bookmark on reddit.com
Posts related to this one:

    * Cited in Bangalore - How cool is that?
    * Inspiration for a RentaCoder listing
    * Stealing Blog Content for Fun and Profit

This entry was posted on Sunday, July 23rd, 2006 and is filed under Industry, trogger.de, Django. You can follow any responses to this entry through the RSS 2.0 feed. You can leave a response, or trackback from your own site.
55 Responses to “Video Blogging using Django and Flash(tm) Video (FLV)”

    1. Nick Says:
      July 23rd, 2006 at 10:08 pm

      Great tutorial!

      If I understand correctly, you are doing the reencoding as part of serving the web request, between accepting the submission of the file and finishing the response to the browser? Is it a very long wait, and do you have problems with timeouts, or is ffmpeg fast enough for whatever size of video you’re accepting?

      I’ll be especially interested to hear about the details if you ever decide to decouple the processing of the video from the request/response cycle of the web interface, as I’m interested in what sort of help Django provides for starting and interfacing with long(er)-running processes. Actually, I’m curious about how people would do it on any framework :) .

      It’s just too bad that doing this reencoding legally in the USA would be difficult and probably requires licenses from countless patent holders :( . (Is that “-acodec mp3″ option to ffmpeg optional, or maybe not actually encoding the audio in MP3? Because I think that the MP3 patent holder demands license fees for use of MP3 encoders. And I suppose the .flv format has a few patents applicable to it too.)

      I certainly like mplayer as a video player and have used it to convert audio codecs on the command line before (and imagine video isn’t much harder), and it certainly supports a lot of video codecs (some through use of ffmpeg), but I don’t know which are actually legal to use (some are ripped out of various win32 applications, which might cause legal problems if a website got too much attention; but then again FFMpeg sounds like it has potential problems too, though only of a patent/reverse-engineering nature instead of a copyright/license-agreement nature).

      I think you should check out PyMedia which is a python wrapper for the libraries which are part of ffmpeg. I think it wraps enough to even do the re-encoding directly in python (but maybe a little more slowly than letting C-code handle the file operations in addition to the video re-encoding). This discussion mentions some other python libraries for dealing with video, though I’ve never really looked at any of the others.

      Anyway, I look forward to future django posts from you!
    2. Simon Says:
      July 24th, 2006 at 4:37 pm

      About FFMpeg patents/reverse-engineering problems, they only affect users from countries with barbarian laws such as DMCA (ie the US, Canada and Japan, afaik). FFmpeg is an European product, it is freely developed and hosted there. As long as there is no software patenting in Europe, it’s all good. I guess you’re American, well you can still get it and use it illegally. Of course, if you do it in a corporate environment, you may have some problems. The solution is: call your representatives, take part in the anti-sw patents lobby.
    3. Daniel Tietze Says:
      July 24th, 2006 at 4:49 pm

      Simon - thanks for clearing that up! I was thinking along the same lines. I’m German. So we narrowly escaped process/software patents once, but the issue keeps coming up again and again and again.

      Everbody interested should check out http://www.nosoftwarepatents.com/
    4. http://www.fabianrodriguez.com Says:
      July 24th, 2006 at 4:53 pm

      Very interesting. I’d like to suggest you also provide Ogg Theora as a format for inline viewing,perhaps with the Cortado applet viewer from Fluendo. Ogg Theora is free + open format which would make your videos more universally / easily readable.

      Transcoding from AVI to Ogg Theora is most easy with ffmpeg2theora :
      http://www.v2v.cc/~j/ffmpeg2theora/

      Extracting metadata from Ogg Theora files may be done with ogginfo in command line.

      Many fine resources about Ogg Theora can be found with Google or at http://del.icio.us/search/?all=theora
    5. Jason Toffaletti Says:
      July 25th, 2006 at 5:34 am

      Flashticle might be better than flvtool.

      http://undefined.org/python/#flashticle

      If you’re using python2.4 you should the subprocess module instead of commands for security reasons.

      Nick asked:
      “I’m interested in what sort of help Django provides for starting and interfacing with long(er)-running processes. Actually, I’m curious about how people would do it on any framework”

      Twisted[1] is very good for this type of job, it is a framework designed for asynchronous programming. Nevow[2] is a nice web framework that integrates with Twisted. Using Nevow’s Athena you could even report back to the client when the video de/encoding process has completed.

      [1] http://twistedmatrix.com
      [2] http://divmod.org/trac/wiki/DivmodNevow
    6. Daniel Tietze Says:
      July 25th, 2006 at 8:08 am

      Jason — those are very good tips, thanks a lot! I’ll be sure to check out Twisted, since I have the feeling that I *will* have to move the encoding out of the Web loop for performance reasons (esp. with longer videos).
      I’m not too sure what Apache/mod_python does to a Python request which returned a Web page but spawned a subprocess. But I’ll investigate.
      The simplest architecture I was envisioning was just calling the conversion process in the background ( “nohup ffmpeg […) &” ), having a reloading view which checks for availability of the file and produces the appropriate response. Not *too* elegant a solution, but I think it could probably be done in quite a robust way.

      As for Flashticle, I had a look through the Web site but it didn’t tell me what flashticle actually *does*. It says it’s “implementing various Macromedia Flash related data formats and protocols.” and it shows me a spec of the FLV format. But why? And what for? And what can I do with it?
    7. t3knoid’s cyberlog » Video Blogging using Django and Flash Video (FLV) Says:
      July 25th, 2006 at 8:33 pm

      […] Maybe someday, I’ll have the time to putting a Drupal module together using these methods.read more | digg story –> […]
    8. Campbell Says:
      July 27th, 2006 at 11:13 am

      I made Videmo.co.nz …..and using mailenable as an email server you can launch applications on recieving emails…..so you can have a email you mobile videos to your blog.
      Take 3gp files in and use FFmpeg to make flvs. I wrapped a c# app to handel the input of data into a database and made a small Ruby on rails site to view it.

      I also managed to get a lightbox like video pop-up which works ok…but it uncovered a few bugs of the flash player 8. Check out the java script if you want it.

      Cheers

      Campbell
    9. Campbell Says:
      July 27th, 2006 at 11:14 am

      P.S. its super slow cause its on a server in my cupboard and on my home connection.
    10. Un “You Tube” 100% OpenSource — Ouvert 24 heures - Verres stérilisés Archive Says:
      July 27th, 2006 at 6:12 pm

      […] La recette demande un peu de bidouillage, mais le résultat est plus qu’intéressant. Sûrement que le tout s’adapte à d’autres CMS et outils de blogue. Via Flashinsider […]
    11. Yet Another Blog from Luar » FFmpeg usage command Says:
      July 28th, 2006 at 4:59 am

      […] Video Blogging using Django and Flash(tm) Video (FLV)   […]
    12. eLearning Skinny » Blog Archive » Shall We Roll Our Own YouTube for BarCamp Vancouver? Says:
      July 28th, 2006 at 1:03 pm

      […] I pointed to this ‘roll your own open source YouTube’ post from Flash Insider (a summary of this original concept from Daniel’s Random Mutterings). […]
    13. Dotpod — ¿Cómo crear tu propio YouTube? Says:
      July 28th, 2006 at 6:26 pm

      […] Un post reciente en el Blog Daniel’s Random Mutterings explica detalladamente cómo hacerlo. Mediante herramientas Open Source como el Djano CMS System, FFMpeg para la conversión en FLV, el FLVtools2 para escribir la información META y el FlowPlayer para embeber el swf, tendrás todo para comenzar a hacerlo. […]
    14. Eric Kersten Weblog » Blog Archive » Crea tu propio YouTube Says:
      July 30th, 2006 at 4:34 am

      […] El link aca: http://blog.go4teams.com/?p=56 […]
    15. Evert Says:
      July 31st, 2006 at 4:41 pm

      FFMpeg now supports FLV 1.1, so you don’t need the FLVTool2 part anymore.. I wrote a small entry about this
    16. felipeandrade.org » “You tube” 100% Open Source Says:
      July 31st, 2006 at 5:45 pm

      […] Você pode encontrar mais detalhes no link abaixo: http://blog.go4teams.com/?p=56 […]
    17. EveryDigg » Blog Archive » Video Blogging using Django and Flash Video (FLV) Says:
      August 3rd, 2006 at 6:06 pm

      […] "The whole process is surprisingly simple and straightforward and can be done entirely with free (FLOSS) tools." A pretty straighforward guide. read more | digg story […]
    18. nooree style » Blog Archive » How to create your own YouTube site Says:
      August 5th, 2006 at 12:54 am

      […] Have you ever wanted to know how you can create your own video hosting site allowing users to upload video, utomatically convert it to FLV, and display it for the world to see? A recent post at Daniel’s Random Mutterings (DRM - how clever) explains exactly how to do this with open source tools. […]
    19. Sebastian Says:
      August 5th, 2006 at 7:49 am

      Hola a todos, viendo que estan utilizando tecnologia flv para video, pueden visitar esta web que usamos esa tecnologia y tienen un js a mano para descargar.
    20. www.blogmemes.net Says:
      August 19th, 2006 at 7:32 am

      Your own youtube like hosting service ?

      Liked what you just read here ? Vote for it on Blogmemes ! The whole process of adding Flash-based (FLV) video blogging support is surprisingly simple and straightforward and can be done entirely with free (FLOSS) tools.
    21. Jimleouf Says:
      August 22nd, 2006 at 2:43 pm

      Hi there,
      I just start with Django and i’m still not familiar with it.
      I tried to follow the guide but I still got errors, if one of you who successe to deploy this have some time, i’ll appreciate the help.
      jimleouf_at_gmail.com
      Thanks

      Jimleouf
    22. franky Says:
      August 24th, 2006 at 7:52 am

      i tried your flv conversion setting, but video quality is not so good when compared with “flash 8 video encoder”..
      is there any settings that can improve the video quality?

      i have “-b 1000 -ar 44100 -ab 64 -s 750×600″

      thanks
    23. spam: the other white meat » A Drupal youtube Site Recipe Says:
      September 12th, 2006 at 4:06 am

      […] Video Blogging using Django and Flash(tm) Video (FLV) […]
    24. Tech Industry » Video Blogging using Django and Flash Video (FLV) Says:
      September 13th, 2006 at 10:52 am

      […] “The whole process is surprisingly simple and straightforward and can be done entirely with free (FLOSS) tools.” A pretty straighforward guide. read more | digg story […]
    25. Samuel J. Greear Says:
      September 25th, 2006 at 9:14 pm

      Great writeup. From experience doing this sort of thing mplayer/mencoder will do a better job on the multiple formats front if you take enough time to sift through and find the proper command line options. It is a wrapper around ffmpeg and others. AFAIK ffmpeg still does not support the newest WMV formats, mencoder can handle them.

      On a similar front we have recently rolled out a tool to facilitate instant video blogging from a webcam, and would be honored if you would check it out. http://flixn.com/ .. and http://flixn.com/developers/
    26. Daniel Tietze Says:
      September 25th, 2006 at 9:22 pm

      I had a quick look at flixn.com — The start page greets me with the need to have the “latest Flash plugin” and not very much else.
      As a Linux/Firefox user that’s pretty much a deal-killer right there.
    27. Samuel J. Greear Says:
      September 25th, 2006 at 9:30 pm

      Daniel, as a (primarily) BSD/Firefox user, I feel your pain. I’m actually hacking away at the templates right now as it has become painfully obvious that the “not much else” is a problem. As to flash, fortunately Flash9 for Linux appears to be looming near.
    28. Tim Says:
      September 27th, 2006 at 10:10 am

      Great stuff!!
      This tutorial is just awesome! I was just wondering, will you get it updated with the comments/suggestions as to what command line is best to use, and so on…?

      Also, flixn is great :-)
    29. Daniel Tietze Says:
      September 27th, 2006 at 3:15 pm

      We have a long weekend coming up in Germany. I’ll maybe try and get something updated.
    30. Colin Esbensen Says:
      October 1st, 2006 at 4:21 am

      Hey Daniel,

      I’m trying to get the Flow Player to work on myspace. I just hate the ads for youtube and so on. Plus I want to be able to control the quality of the product. I’ve been at this for a week now and have gotten no where. I hit the wall and I’d have pulled out all my hair by now if I had any. : ) I wouldn’t ask if I wasn’t at my wits end, but could you help me.

      Cheers, Colin
    31. gumango Says:
      October 19th, 2006 at 9:03 am

      To convert any file format you can use mencoder rather than ffmpeg. But with mencoder we have problem with 3gp files audio. Mainly because of the AMR codec support issue. But you can use mencoder for most of the video formats and only for 3gp you can use ffmpeg.
    32. Pradeep B V Says:
      December 2nd, 2006 at 9:53 pm

      Hey Daniel,

      I have used parts of your post for my presentation at BarCampBangalore.

      Thanks a ton.
    33. creating a You tube or streaming server - MacNN Forums Says:
      December 8th, 2006 at 3:42 pm

      […] Link dump Using Lighttpd, Mplayer/Mencoder and Flvtool2 to Implement Flash Video Streaming :: Homo-Adminus Blog by Alexey Kovyrin Video Blogging using Django and Flash(tm) Video (FLV) � DRM - Daniel’s Random Mutterings digg - How to create your own Youtube and get your own billion Eh some i found. I looked for Rails version since I am versed n Rails now instead of python but if you have any leads they would be much appreciated. […]
    34. Internet and Network Art » FFMPEG Says:
      December 9th, 2006 at 9:30 pm

      […] http://www.jessewarden.com/archives/2006/09/serverside_ffmpeg.html […]
    35. Video konvertierung mittels php & apache wie in youtube - PHP @ tutorials.de: Forum - Tutorials - Hilfe - Schulung & mehr Says:
      January 10th, 2007 at 11:31 pm

      […] AW: Video konvertierung mittels php & apache wie in youtube Hey, siehe hier: http://blog.go4teams.com/?p=56 In dem Artikel wird zwar die Benutzung von Django beschrieben, l�sst sich aber auch Ruby bzw. RubyonRails �bertragen. Mit PHP ist die L�sung nicht und ich denke auch nicht, dass es irgendwelche L�sungen geben wird mittels PHP und anderen Tools Videos in FLV umzuwandeln. Zitat: […]
    36. mcdave.net » links for 2007-01-20 Says:
      January 24th, 2007 at 2:14 pm

      […] Video Blogging using Django and Flash(tm) Video (FLV) » DRM - Daniel’s Random Mutterings (tags: video flash django tutorial python flv) […]
    37. Digital Motion dot net » Some flashy goodness for your Tuesday morning Says:
      January 30th, 2007 at 3:45 pm

      […] Finally, Daniel Tietze tell you how to make your own uTube. –> […]
    38. Realizzare un Clone di YouTube « Scaracco Says:
      March 10th, 2007 at 12:46 pm

      […] Ispirazione: Video Blogging using Django and Flash(tm) Video (FLV) […]
    39. FLV converter Says:
      March 16th, 2007 at 2:08 pm

      […] Finally, FLV converter tell you how to make your own uTube. –> […]
    40. FLV converter Says:
      March 16th, 2007 at 2:18 pm

      Great Post, now it would be nice to convert some WMV files that are conflictive to get absolutely transparent to the user, any ideas?

      Greets…
    41. FLV converter Says:
      March 16th, 2007 at 2:29 pm

      FFMpeg now supports FLV 1.1, so you don’t need the FLVTool2 part anymore.. I wrote a small entry about this . AS far AS I know, it may has update to 1.2
    42. Jack Says:
      March 30th, 2007 at 2:48 pm

      Hi Daniel,

      I met a problem when I was trying to use your code. I put Flowplayer and my video in the same folder. I can load Flowplayer but can’t load the video file. So there is always a blank screen. I am using Ubuntu+Apache2. Already did the housekeeping stuff. I am a newbie and searched google, so you are the last man I can ask. Thanks!
    43. David Lavoie Says:
      April 18th, 2007 at 8:23 pm

      I had an issue using FFMPEG with linux.
      Basically on errors, i would get a constant stream of errors in my apache log files, filling the hard drive (up to like 60gigs or repeated errors).

      Anyone else have this issue? ever?
      Any idea how to ensure that the output of FFMPEG run by PHP could be redirected to /dev/null or somthing?
    44. Zalapao Press » Blog Archive » FFmpeg usage command Says:
      June 5th, 2007 at 11:00 am

      […] Video Blogging using Django and Flash(tm) Video (FLV) […]
    45. iGloo Says:
      June 21st, 2007 at 4:03 am

      Hi there.

      You should try mencoder wich use FFMPEG for some part of the conversion, the only thing is MEncoder quality will be much higher than FFMPEG alone.

      As for the video conversion, i spawn a SH script in the background to do the work. I wrote a upload handler script in both perl and php.

      To get WMV/MPEG/etc conversion, go to Mencoder website and get the essential codec pack. It is a collection of freely available binaries Mencoder can use to encode/read.

      Here the revelant mencoder part:

      #!/bin/sh
      nice /usr/local/bin/mencoder -o .flv -of lavf -ovc lavc -oac lavc -lavfopts i_certify_that_my_video_stream_does_not_use_b_frames \
      -lavcopts vcodec=flv:autoaspect:vbitrate=350:v4mv:vmax_b_frames=0:vb_strategy=1:mbd=2:mv0:trell:cbp:sc_factor=6:cmp=2:subcmp=2:predia=2:dia=2:preme=2:turbo:acodec=mp3:abitrate=56 \
      -vf scale=320:240 -srate 22050 -af lavcresample=22050

      /usr/local/bin/flvtool2 -U .flv
    46. pat Says:
      June 27th, 2007 at 11:07 pm

      how the heck am i supposed to comprehend this crap!! make it for 2 year olds to understand and then we will get somewhere! ok thank you
    47. links for 2007-07-06 « PaxoBlog Says:
      July 10th, 2007 at 4:05 pm

      […] Video Blogging using Django and Flash(tm) Video (FLV) » DRM - Daniel’s Random Mutterings I just added Flash-based (FLV) video blogging support to my Django-powered travel portal site, trogger.de. The whole process is surprisingly simple and straightforward and can be done entirely with free (FLOSS) tools. (tags: django video blog theory overview flash youtube related) […]
    48. Michael Says:
      July 11th, 2007 at 7:42 pm

      Thanks for this!

      Worked really great (only getting ffmpeg to work with mp3 was a little bit tricky on my debian system. In the end I just recompiled ffmpeg from source.. see here http://blog.gwikzone.org/articles/2006/09/25/flv-encoding-with-ffmpeg also the option changed and copied manually libmp3lame.so.0 to the right location)

      I really start to like django…
    49. Alce Says:
      July 23rd, 2007 at 3:26 am

      Awesome post (and comments). Although I am not familiar with Django, the process you posted here fits perfectly with what I am trying to achieve, regardless of language or framework. You just saved me some 6+ hours of browsing to gather all the info I needed. Thanks a bunch.
    50. HenrikG Says:
      August 3rd, 2007 at 2:59 pm

      I had some problems getting ffmpeg to work with mp3 encoding on Ubuntu Linux. First configuration:
      ./configure –enable-gpl –enable-pp –enable-libfaad –enable-libvorbis –enable-libogg –enable-liba52 –enable-dc1394 –enable-libgsm –enable-libmp3lame –enable-libfaac –enable-libxvid –enable-pthreads –enable-libx264

      The problem occured when I compiled ffmpeg with “make”:

      Imlib2.h:108: error: syntax error before “*” token

      I solved this by installing Imlib2 from source:
      href=”http://sourceforge.net/project/showfiles.php?group_id=2
      (check at the bottom of the page)

      I also installed a lot of libs to get the compilation to work:

      apt-get build-dep ffmpeg
      apt-get install liblame0 liblame-dev libtool libpng3 libpng3-dev libttf-dev cdbs libbz2-dev libid3tag0 libid3tag0-dev xlibs-dev libxvidcore4-dev libx264-dev libfaac-dev libfaad2-dev
    51. Plantillas para Blogger, recursos y herramientas » Como crear tu propio Youtube y ganar dinero en internet añadiendo Video Ads. Says:
      November 18th, 2007 at 7:39 pm

      […] En el blog Daniel’s Random Mutterings se explica paso a paso cómo montar un servicio de alojamiento, gestión y reproducción que permita a los usuarios subir y compartir sus vídeos con el resto de internautas. El proceso no es muy complicado a pesar de que no había oído hablar nunca de las herramientas mencionadas en el artículo, como por ejemplo el CMS Django, pero desde mi punto de vista el resultado final tiene un valor más bien pobre en cuanto a su personalización y diseño al gestionarse a través del portal gratuito Trogger.de. También es necesario contar con una herramienta para convertir los archivos al formato FLV (FFMpeg), la utilidad FLVtools2 para añadir la meta información y el reproductor Flowplayer para incrustar los archivos SWF de flash. […]
    52. Video Blog mit TYPO3? - TYPO3forum.net Says:
      November 20th, 2007 at 12:31 pm

      […] permalink Hallo allerseits, Ich sehe mir gerade Blog Extensions von TYPO3 an. Ziel w�re eine Art Video Blog a la YouTube. Im TER finden sich ja timtab, timtab_embeddedvideo. Einige interessante Extensions w�ren auch bddb_flvvideogallery, flvplayer. Es g�be ja einige OpenSource Tools f�r Flash Video: FFMpeg (f�r Video Umkodierung von MPEG,AVI,Quicktime, etc FLV) FLVtools2, mplayer, etc (f�r Video Metadaten) Beim Recherchieren bin ich noch auf einen Artikel gesto�en: Video Blogging using Django and Flash(tm) Video (FLV) Was haltet ihr vom Thema Video Blog mit TYPO3? […]
    53. How to create your own YouTube site Says:
      December 14th, 2007 at 6:38 pm

      […] A recent post at Daniel’s Random Mutterings explains how to do this with open source tools. Filed Under Design & development […]
    54. FFmpeg usage command | Gone with the wind Says:
      January 28th, 2008 at 3:25 pm

      […] Video Blogging using Django and Flash(tm) Video (FLV) […]
    55. Proposal - Video Blogger for Cat Facts! » PAWSit Says:
      February 14th, 2008 at 10:11 pm

      […] Create Your Own YouTube […]

Leave a Reply

Name (required)

Mail (will not be published) (required)

Website

DRM - Daniel’s Random Mutterings -- powered by WordPress
Entries (RSS) and Comments (RSS).
"""

    thumbnailfilename = ''.join(os.path.splitext(sourcefile)[0] + '.png')
    ffmpeg = "ffmpeg -i %s -acodec mp3 -ar 22050 -ab 32 -f flv -s %s %s" % (sourcefile, convert2size, targetfile)
    grabimage = "ffmpeg -y -i %s -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320x240 %s " % (
        sourcefile, thumbnailfilename)
    flvtool = "flvtool2 -U %s" % targetfile
    try:
        ffmpegresult = subprocess.Popen(ffmpeg, shell=True, bufsize=1024, stdout=subprocess.PIPE).stdout
        flvresult = subprocess.Popen(flvtool, shell=True, bufsize=1024, stdout=subprocess.PIPE).stdout
        grab = subprocess.Popen(grabimage, shell=True, bufsize=1024, stdout=subprocess.PIPE).stdout
    except:
        print(sys.exc_info())
        return sys.exc_info[1]
    return None
